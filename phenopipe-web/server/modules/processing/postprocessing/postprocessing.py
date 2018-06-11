import grpc
from graphql_relay import to_global_id

from server.extensions import db, get_r_channel, \
    postprocess_task_scheduler
from server.gen import phenopipe_r_pb2_grpc, phenopipe_r_pb2
from server.models import SnapshotModel, SampleGroupModel, AnalysisModel, PlantModel
from server.modules.processing.exceptions import AlreadyFinishedError, AnalysisDataNotPresentError
from server.modules.processing.remote_exceptions import UnavailableError, \
    PostprocessingStackAlreadyExistsError, NotFoundError


def submit_postprocesses(analysis, postprocessing_stack_ids, note, username, depends_on=None):
    """
    Creates and submits multiply postprocessing jobs and puts them into the RQ for the workers to process

    :param analysis: Either the ID or an Instance of :class:`~server.models.analysis_model.AnalysisModel`
    :param postprocessing_stack_ids: A List of Postprocessing Stack ids indicating which stacks
        should be applied to the given analysis results
    :param note: A note from the user to make it easier to identify postprocesses
    :param username: The name of the current user issuing the postprocessing jobs
    :param depends_on: A job which must be finished before any postprocess can be executed

    :return: A dict containing a list of status IDs, a list of the generated RQ jobs
        and a list of stack IDs which where already applied
    """
    if not isinstance(analysis, AnalysisModel):
        analysis = db.session.query(AnalysisModel).get(analysis)
    if analysis.export_path is not None:
        snapshots_query = db.session.query(SnapshotModel).filter(SnapshotModel.timestamp_id == analysis.timestamp.id) \
            .filter(SnapshotModel.excluded == False)
        control_group = snapshots_query \
            .join(PlantModel) \
            .join(SampleGroupModel) \
            .filter(SampleGroupModel.is_control == True) \
            .first().plant.sample_group

        tasks = []
        finished = []
        postprocesses = []

        experiment = analysis.timestamp.experiment
        stacks = []
        for stack_id in postprocessing_stack_ids:
            try:
                stacks.append(get_postprocessing_stack(username, stack_id))
            except NotFoundError:
                raise
            except UnavailableError:
                raise

        for stack in stacks:
            try:
                task, postprocess = postprocess_task_scheduler.submit_task(analysis, snapshots_query.all(),
                                                                           control_group, stack, note,
                                                                           username,
                                                                           experiment, depends_on)
                tasks.append(task)
                postprocesses.append(postprocess)
            except AlreadyFinishedError as e:
                finished.append(to_global_id(e.schema_name, e.db_id))
        return tasks, postprocesses, finished
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


def get_postprocessing_stack(username, stack_id):
    """
    Fetches the Postprocessing Stack with the given ID and username from the postprocessing server

    :param stack_id: The ID of the stack to fetch

    :param username: The username of the user who owns this stack

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
