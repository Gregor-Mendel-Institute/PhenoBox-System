from datetime import datetime

import grpc
from rq.decorators import job
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager

from server.extensions import redis_db
from server.gen import phenopipe_r_pb2_grpc, phenopipe_pb2_grpc, phenopipe_r_pb2, phenopipe_pb2
from server.models import PostprocessModel, SampleGroupModel, PlantModel, SnapshotModel
from server.modules.postprocessing.postprocessing_jobs.job_type import JobType
from server.modules.postprocessing.postprocessing_jobs.worker_extensions import get_status_cache, get_grpc_channel, \
    get_session
from server.utils.redis_status_cache.status import Status


def create_return_object(type, analysis_id, response):
    """
    Convenience method to create a proper return object for the RQ Job function

    :param type: The type of the Job. Instance of :class:`~server.modules.postprocessing.postprocessing_jobs.job_type.JobType`
    :param analysis_id: The ID of the processed :class:`~server.models.analysis_model.AnalysisModel` instance
    :param response: A dict containing return values that are job specific

    :return: A dict containing the given values with the keys: 'type', 'analysis_id', 'response'
    """
    ret = dict()
    ret['type'] = type
    ret['analysis_id'] = analysis_id
    ret['response'] = response
    return ret


def update_status_object(username, status_id, current_status=None, current_message=None, jobs=None):
    """
    Fetches the status object with the given ID from the postprocessing
    :class:`~server.utils.redis_status_cache.redis_status_cache.StatusCache` and applies the given changes

    :param username: The username to which the :class:`~server.utils.redis_status_cache.status_object.StatusObject` belongs
    :param status_id: The ID of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param current_status: The new status to be set. If None the old value will remain.
    :param current_message: The new message to be set. If None the old value will remain.
    :param jobs: The new job list to be set. If None the old value will remain.

    :return: None
    """
    postprocessing_status_cache = get_status_cache()
    status = postprocessing_status_cache.get(username, status_id)
    if current_status is not None:
        status.current_status = current_status
    if current_message is not None:
        status.current_message = current_message
    if jobs is not None:
        for name, job_id in jobs.items():
            status.add_job(name, job_id)
    try:
        postprocessing_status_cache.update(username, status)
    except KeyError:
        # Can happen if the cache eviction is triggered before the job tries to update the status
        pass


@job('postprocessing', connection=redis_db)
def invoke_r_postprocess(experiment_name, postprocess_id, analysis_id, excluded_plant_names, path_to_report, postprocessing_stack_id,
                         status_id,
                         username):
    """
    This Methods represents an RQ Job workload. It should be enqueued into the RQ Postprocessing Queue and processed by an according worker

    Handles the invokation of a postprocess on the postprocessing server and fetches the result information afterwards.
    The received information is then entered into the database accordingly

    :param experiment_name: The name of the experiment this postprocess belongs to
    :param postprocess_id: The ID of this postprocess
    :param analysis_id: The ID of the analysis to be postprocessed
    :param excluded_plant_names: The full names (Used as ID by IAP) of all excluded plants
    :param path_to_report: The path to the export path of the analysis. (The folder where the report file of IAP is saved)
    :param postprocessing_stack_id: The ID of the stack which should be used for postprocessing
    :param status_id: The ID of the status object in the :class:`~server.utils.redis_status_cache.redis_status_cache.StatusCache`
    :param username: The username of the user issuing this request

    :return: A dict containing the 'path_to_results', the used 'postprocessing_stack_id' and a timestamps 'started_at' and 'finished_at'
         (All nested inside the 'response' key)
    """
    print('EXECUTE POSTPROCESS')
    # TODO supply the name of the stack for better messages
    # update_status_object(username, status_id, Status.running,
    #                     'Started Postprocessing Stack "{}"'.format(postprocessing_stack_name), {'postprocess': job.id})
    # update_status_object(username, status_id, Status.running,
    #                     'Started Postprocessing Stack "{}"'.format(postprocessing_stack_id))
    channel = get_grpc_channel()
    r_stub = phenopipe_r_pb2_grpc.PhenopipeRStub(channel)
    pipe_stub = phenopipe_pb2_grpc.PhenopipeStub(channel)
    session = get_session()
    postprocess = session.query(PostprocessModel).get(postprocess_id)
    try:
        started_at = datetime.utcnow()
        postprocess.started_at = started_at
        session.commit()
        control_group = session.query(SampleGroupModel) \
            .join(PlantModel) \
            .join(SnapshotModel,
                  and_(
                      SnapshotModel.plant_id == PlantModel.id,
                      SnapshotModel.postprocesses.any(PostprocessModel.id == postprocess.id)
                  )) \
            .options(
            contains_eager("plants"),
            contains_eager("plants.snapshots"),
        ).filter(SampleGroupModel.is_control == True) \
            .first()
        meta = phenopipe_r_pb2.PostprocessingMetadata(experiment_name=experiment_name,control_treatment_name=control_group.treatment)
        response = r_stub.PostprocessAnalysis(
            phenopipe_r_pb2.PostprocessRequest(path_to_report=path_to_report,
                                               postprocess_stack_id=postprocessing_stack_id,
                                               snapshot_hash=postprocess.snapshot_hash,
                                               meta=meta,
                                               excluded_plant_identifiers=excluded_plant_names)
        )
        job_id = response.job_id
        request = phenopipe_pb2.WatchJobRequest(
            job_id=job_id
        )
        status = pipe_stub.WatchJob(request)
        postprocessing_status_cache = get_status_cache()
        for msg in status:
            #update_status_object(username, status_id, current_message=msg.message.decode('string-escape'))
            postprocessing_status_cache.log(status_id, msg.message.decode('string-escape'), msg.progress)

        response = r_stub.FetchPostprocessingResult(
            phenopipe_pb2.FetchJobResultRequest(job_id=job_id)
        )
        finished_at = datetime.utcnow()
        postprocess.finished_at = finished_at
        update_status_object(username, status_id, current_status=Status.finished, current_message="Completed")
        postprocess.result_path = response.path_to_results
        session.commit()
        # update_status_object(username, status_id, current_status=Status.finished,
        #                     current_message='Finished Postprocessing Stack "{}"'.format(postprocessing_stack_id))
        return create_return_object(JobType.r_postprocess, analysis_id, {'path_to_results': response.path_to_results,
                                                                         'postprocess_stack_id': postprocessing_stack_id,
                                                                         'started_at': started_at,
                                                                         'finished_at': finished_at})
    except grpc.RpcError as e:
        session.delete(session.query(PostprocessModel).get(postprocess.id))
        session.commit()
        # TODO put error message into log
        update_status_object(username, status_id, current_status=Status.error,
                             current_message=e.details())
        print(e.details())
        raise
    except DBAPIError as err:
        # TODO handle this
        print(err.message)
        session.rollback()
        raise
        # TODO raise error or return something
