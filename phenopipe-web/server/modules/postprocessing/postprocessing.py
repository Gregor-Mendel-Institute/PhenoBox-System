import grpc
from graphql_relay import to_global_id
from rq.job import Job

from server.extensions import db, postprocessing_status_cache, redis_db, postprocessing_job_queue, get_r_channel
from server.gen import phenopipe_r_pb2_grpc, phenopipe_r_pb2
from server.models import PostprocessModel, SnapshotModel, SampleGroupModel
from server.modules.postprocessing.postprocessing_jobs import invoke_r_postprocess
from server.modules.processing.exceptions import AlreadyFinishedError, AlreadyRunningError, AnalysisDataNotPresentError
from server.modules.processing.remote_exceptions import UnavailableError, \
    PostprocessingStackAlreadyExistsError, NotFoundError
from server.utils.redis_status_cache.redis_status_cache import StatusCache
from server.utils.redis_status_cache.status import Status
from server.utils.redis_status_cache.status_object import StatusObject


def is_job_running_for(analysis_id):
    """
   Checks if there is currently a postprocess running for the given analysis

   :param analysis_id: The ID of the analysis to look up

   :return: True if there is a job which postprocesses the given analysis. False otherwise.
   """
    identifiers = postprocessing_status_cache.get_all_identifiers()

    for identifier in identifiers:
        if is_job_running_for_user(identifier, analysis_id):
            return True
    return False


def is_job_running_for_user(username, analysis_id):
    """
    Checks if there is currently a postprocess running for the given analysis which has been issued by the given user

    :param username: The username of the User who has started the postprocesing job
    :param analysis_id: The ID of the analysis to look up

    :return: True if there is a job from the given user which postprocesses the given analysis. False otherwise
    """
    status_list = postprocessing_status_cache.get_all(username)
    for status_id in status_list:
        status_key_info = StatusCache.from_id(status_id)
        # Key format for analysis status '[analysis_id]:[stack_id]:[snapshot_hash]
        if status_key_info[0] == analysis_id:
            return True
    return False


def submit_postprocess(session, analysis, stack_id, note, username, experiment):
    """
    Creates a Background Job for running a specific postprocessing stack on an analysis result and enqueues it.
    It additionally creates a :class:`~server.utils.redis_status_cache.status_object.StatusObject` for this Job and adds it to the StatusCache.

    The Job will only be enqueued if there is no corresponding entry in the 'postprocess' table and
    the method :meth:`~server.utils.redis_status_cache.redis_status_cache.StatusCache.checked_put()` returns True.

    :param session: The SQLAlchemy database session
    :param analysis: The :class:`~server.models.analysis_model.AnalysisModel` instance to be postprocessed
    :param stack_id: The ID of the Postprocessing stack that should be used
    :param note: A note from the user to make it easier to identify a postprocess
    :param username: The username of the experiment owner
    :param experiment: The :class:`~server.models.experiment_model.ExperimentModel` to which the data belongs

    :return: A Tuple containing the Status ID and the RQ Job instance
    """
    #TODO additional checks for being sure that IAP ran properly?
    if analysis.export_path is None:
        pass
        #TODO invoke export
    snapshots = session.query(SnapshotModel).filter(SnapshotModel.timestamp_id == analysis.timestamp.id) \
        .filter(SnapshotModel.excluded == False) \
        .all()
    control_group = session.query(SampleGroupModel).filter(SampleGroupModel.experiment_id == experiment.id).filter(
        SampleGroupModel.is_control == True).one()

    postprocess, created = PostprocessModel.get_or_create(analysis.id, stack_id, control_group.id, snapshots, session)
    if created:
        postprocess.note = note
        s_hash = PostprocessModel.calculate_snapshot_hash(snapshots)
        status_id = StatusCache.generate_id(str(analysis.id), stack_id,
                                            str(s_hash))

        status_name = 'Postprocess IAP analysis'
        # TODO use the stack name and pipeline name
        status_description = 'Apply postprocessing stack "{}" to results of analysis for experiment "{}" at timestamp({}) with pipeline "{}".'.format(
            stack_id, experiment.name,
            analysis.timestamp.created_at.strftime("%a %b %d %H:%M:%S UTC %Y"), analysis.pipeline_id)
        status = StatusObject(status_name, status_description, status_id, current_status=Status.pending)

        can_run = postprocessing_status_cache.checked_put(username,
                                                          status)
        # TODO not necessary after implementation of PostprocessModel.get_or_create?
        if can_run:
            session.commit()
            excluded_snapshots = session.query(SnapshotModel).filter(
                SnapshotModel.timestamp_id == analysis.timestamp.id) \
                .filter(SnapshotModel.excluded == True) \
                .all()
            excluded_plants = [snapshot.plant.full_name for snapshot in excluded_snapshots]
            postprocessing_job = Job.create(invoke_r_postprocess,
                                            (experiment.name, postprocess.id, analysis.id, excluded_plants,
                                             analysis.export_path,
                                             stack_id, status_id,
                                             username),
                                            connection=redis_db,
                                            result_ttl=-1,
                                            ttl=-1,
                                            description='Run postprocessing stack({}) on the results of analysis ({})'.format(
                                                stack_id,
                                                to_global_id('Analysis', analysis.id)))
            status.add_job('postprocess', postprocessing_job.id)
            try:
                postprocessing_status_cache.update(username, status)
            except KeyError:
                pass  # Cannot happen because of the checked put in the beginning
            postprocessing_job_queue.enqueue_job(postprocessing_job)

            return status_id, postprocessing_job
        else:  # TODO evaluate should not happen because of get_or_create implementation
            db.session.rollback()
            # Currently in progress
            raise AlreadyRunningError(username, status_id,
                                      'The requested postprocessing stack is already running')
    else:
        db.session.rollback()
        # Not exactly. actually it could be still running
        # TODO Check for the finished at column to determine if it is still running or not
        raise AlreadyFinishedError('Postprocess', postprocess.id,
                                   'The requested postprocessing stack has already been processed')


def submit_postprocesses(analysis, postprocessing_stack_ids, note, username, from_worker=False):
    """
    Creates and submits multiply postprocessing jobs and puts them into the RQ for the workers to process

    :param analysis: Instance of :class:`~server.models.analysis_model.AnalysisModel`
    :param postprocessing_stack_ids: A List of Postprocessing Stack ids indicating which stacks
        should be applied to the given analysis results
    :param note: A note from the user to make it easier to identify postprocesses
    :param username: The name of the current user issuing the postprocessing jobs
    :param from_worker: Indicates whether or not this call is coming from a background worker or from the main application

    :return: A dict containing a list status IDs, a list of the generated RQ jobs
        and a list of stack IDs which where already applied
    """
    if analysis.export_path is not None:
        jobs = []
        finished = []
        status_ids = []
        if from_worker:
            # TODO pass in session if from Worker
            from server.modules.analysis.analysis_jobs.worker_extensions import get_session
            session = get_session()
        else:
            session = db.session
        experiment = analysis.timestamp.experiment
        for stack_id in postprocessing_stack_ids:
            try:
                # Only create jobs and don't enqueue them right away to be able to cancel if any job is already running
                status_id, job = submit_postprocess(session, analysis, stack_id, note, username, experiment)
                jobs.append(job)
                status_ids.append(status_id)
            except AlreadyRunningError as e:  # TODO return error if a job is already running?
                status_ids.append(e.status_id)
            except AlreadyFinishedError as e:
                finished.append(to_global_id(e.schema_name, e.db_id))
        return {'status_ids': status_ids, 'jobs': jobs, 'already_finished': finished}
    else:
        raise AnalysisDataNotPresentError(analysis.id,
                                          'No data exported for analysis({})'.format(
                                              to_global_id('Analysis', analysis.id)))


def upload_stack(stack):
    """
    Uploads the given Postprocessing Stack to the Postprocessing server via GRPC

    :param stack: Instance of :class:`server.gen.phenopipe_r_pb2.PostprocessingStack`

    :return: The ID of the uploaded stack
    """
    r_stub = phenopipe_r_pb2_grpc.PhenopipeRStub(get_r_channel())
    try:
        scripts = []
        for index, script in enumerate(stack.scripts):
            scripts.append(phenopipe_r_pb2.PostprocessingScript(name=script.name, description=script.description,
                                                                index=index, file=script.file))
        stack = phenopipe_r_pb2.PostprocessingStack(name=stack.name, description=stack.description,
                                                    author=stack.author, scripts=scripts)
        response = r_stub.UploadPostprocessingStack(
            phenopipe_r_pb2.UploadPostprocessingStackRequest(stack=stack)
        )
        stack_id = response.stack_id
        print(stack_id)

        return stack_id
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Postprocessing Service")
        elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise PostprocessingStackAlreadyExistsError(e.details(), e.initial_metadata()[0][1],
                                                        e.initial_metadata()[1][1])


def get_postprocessing_stack(stack_id, username):
    """
    Fetches the Postprocessing Stack with the given ID from the postprocessing server

    :param stack_id: The ID of the stack to fetch

    :raises NotFoundError: if the requested postprocessing stack is not found

    :raises UnavailableError: if the Postprocessing service is not reachable

    :return: Instance of :class:`server.gen.phenopipe_r_pb2.PostprocessingStack`
    """
    r_stub = phenopipe_r_pb2_grpc.PhenopipeRStub(get_r_channel())
    try:
        response = r_stub.GetPostprocessingStack(
            phenopipe_r_pb2.GetPostprocessingStackRequest(stack_id=stack_id, author=username)
        )

        return response.stack
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise NotFoundError(e.details(), "PostprocessingStack")
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Postprocessing Service")
        raise  # TODO other error options?


def get_postprocessing_stacks(username):
    """
    Fetches all available Postprocessing Stacks from the postprocessing server

    :raises UnavailableError: if the Postprocessing service is not reachable

    :return: List of instances of :class:`server.gen.phenopipe_r_pb2.PostprocessingStack`
    """
    r_stub = phenopipe_r_pb2_grpc.PhenopipeRStub(get_r_channel())
    try:
        response = r_stub.GetPostprocessingStacks(
            phenopipe_r_pb2.GetPostprocessingStacksRequest(author=username)
        )
        stacks = response.stacks
        return stacks
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Postprocessing Service")
        raise  # TODO other error options?
