from datetime import datetime

import grpc
from rq import get_current_job
from rq.decorators import job
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager

from server.extensions import redis_db
from server.gen import phenopipe_r_pb2_grpc, phenopipe_pb2_grpc, phenopipe_r_pb2, phenopipe_pb2
from server.models import PostprocessModel, SampleGroupModel, PlantModel, SnapshotModel
from server.modules.processing.postprocessing.postprocessing_jobs.job_type import JobType
from server.modules.processing.postprocessing.postprocessing_jobs.worker_extensions import get_grpc_channel, \
    get_session, get_redis_connection, get_log_store
from server.modules.processing.postprocessing.postprocessing_task import PostprocessingTask


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


@job('postprocessing', connection=redis_db)
def invoke_r_postprocess(experiment_name, postprocess_id, analysis_id, excluded_plant_names, path_to_report,
                         postprocessing_stack_id, postprocessing_stack_name, username, task_key):
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
    :param username: The username of the user issuing this request

    :return: A dict containing the 'path_to_results', the used 'postprocessing_stack_id' and a timestamps 'started_at' and 'finished_at'
         (All nested inside the 'response' key)
    """
    print('EXECUTE POSTPROCESS')
    job = get_current_job()
    log_store = get_log_store()
    task = PostprocessingTask.from_key(get_redis_connection(), task_key)
    log_store.put(job.id, 'Started Postprocessing Job', 0)
    task.update_message('Started Postprocessing Job')
    channel = get_grpc_channel()
    r_stub = phenopipe_r_pb2_grpc.PhenopipeRStub(channel)
    pipe_stub = phenopipe_pb2_grpc.PhenopipeStub(channel)
    session = get_session()
    # TODO get parameters from postrpocess object instead of via function parameters
    postprocess = session.query(PostprocessModel).get(postprocess_id)
    try:
        started_at = datetime.utcnow()
        postprocess.started_at = started_at
        session.commit()
        # TODO pass control group in

        meta = phenopipe_r_pb2.PostprocessingMetadata(experiment_name=experiment_name,
                                                      control_treatment_name=postprocess.control_group.treatment)
        response = r_stub.PostprocessAnalysis(
            phenopipe_r_pb2.PostprocessRequest(path_to_report=path_to_report,
                                               postprocess_stack_id=postprocessing_stack_id,
                                               snapshot_hash=postprocess.snapshot_hash,
                                               meta=meta,
                                               excluded_plant_identifiers=excluded_plant_names)
        )
        task.update_message('Started Postprocessing Stack "{}"'.format(postprocessing_stack_name))
        log_store.put(job.id, 'Started Postprocessing Stack "{}"'.format(postprocessing_stack_name), 0)
        remote_job_id = response.job_id
        request = phenopipe_pb2.WatchJobRequest(
            job_id=remote_job_id
        )
        status = pipe_stub.WatchJob(request)
        for msg in status:
            log_store.put(job.id, msg.message.decode('string-escape'), msg.progress)

        response = r_stub.FetchPostprocessingResult(
            phenopipe_pb2.FetchJobResultRequest(job_id=remote_job_id)
        )
        finished_at = datetime.utcnow()
        postprocess.finished_at = finished_at
        task.update_message('Finished Postprocessing Job')
        log_store.put(job.id, 'Finished Postprocessing Job', 100)
        postprocess.result_path = response.path_to_results
        session.commit()
        return create_return_object(JobType.r_postprocess, analysis_id, {'path_to_results': response.path_to_results,
                                                                         'postprocess_stack_id': postprocessing_stack_id,
                                                                         'started_at': started_at,
                                                                         'finished_at': finished_at})
    except grpc.RpcError as e:
        session.delete(session.query(PostprocessModel).get(postprocess.id))
        session.commit()
        log_store.put(job.id, e.details(), 0)
        task.update_message('Postprocessing Job Failed')
        print(e.details())
        raise
    except DBAPIError as err:
        # TODO handle this
        print(err.message)
        session.rollback()
        log_store.put(job.id, e.details(), 0)
        task.update_message('Postprocessing Job Failed')
        raise
        # TODO raise error or return something
