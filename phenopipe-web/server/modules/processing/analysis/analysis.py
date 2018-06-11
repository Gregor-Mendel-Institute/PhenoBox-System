import os

import grpc
from flask import current_app

from server.extensions import analysis_task_scheduler
from server.gen import phenopipe_iap_pb2_grpc, phenopipe_iap_pb2
from server.modules.processing.exceptions import InvalidPathError, AlreadyFinishedError
from server.modules.processing.remote_exceptions import UnavailableError, PipelineAlreadyExistsError, \
    InvalidPipelineError, InternalError, NotFoundError
from server.utils.util import remove_prefix

iap_meta_cols = [
    'import file',
    'plant ID',
    'replicate',
    'time',
    'time unit',
    'imaging time',
    'measurement tool',
    'camera.position',
    'rotation degree',
    'species',
    'genotype',
    'variety',
    'growth conditions',
    'treatment'
]
_timeout_import = 43200  # 12h
_timeout_analysis = 86400  # 24h
_timeout_export = 300  # 5min


def submit_iap_jobs(timestamp, experiment_name, coordinator, scientist, input_path, output_path, pipeline_id,
                    username):
    """
    Creates and Enqueues the necessary background jobs to import, analyze and export the data of the given timestamp

    :param timestamp: The timestamp to be analyzed
    :param experiment_name: The name of the experiment the timestamp belongs to
    :param coordinator: The name of the experiment coordinator
    :param scientist: The name of the scientist conducting this experiment
    :param input_path: The path, as SMB URL, where the input data (images) are stored
    :param output_path: The path, as SMB URL, where the exported data should be stored
    :param pipeline_id: The ID of the IAP Pipeline which should be used for analysis
    :param username: The username of the User requesting this process

    :raises AlreadyRunningError: If the analysis is currently in progress
    :raises AlreadyFinishedError: If the analysis has already been processed.

    :return: The AnalysisTask object and the analysis object itself
    """
    shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
    smb_url, local_path = next(((smb, path) for smb, path in shared_folder_map.items() if input_path.startswith(smb)),
                               (None, None))
    if local_path is not None:
        local_path = os.path.join(local_path, remove_prefix(input_path, smb_url))

        try:
            pipeline = get_iap_pipeline(username, pipeline_id)
        except NotFoundError:
            raise
        except UnavailableError:
            raise

        try:
            task, analysis = analysis_task_scheduler.submit_task(timestamp, experiment_name, coordinator, scientist,
                                                                 input_path,
                                                                 output_path, pipeline, username, local_path)
            return task, analysis
        except AlreadyFinishedError:
            raise
    else:
        # TODO send another message to user. (Don't return path because it's of no interested to the user)
        # TODO log --> severe, propably needs manual interaction
        raise InvalidPathError(input_path, 'The given input path "{}" is not valid'.format(input_path))


def upload_pipeline(pipeline, username):
    """
    Uploads the given pipeline file to the Analyis/IAP server

    :param pipeline: the pipeline file object

    :raises UnavailableError: if the Analysis/IAP service is not reachable
    :raises PipelineAlreadyExistsError: if a pipeline with the same name is already present on the server
    :raises InvalidPipelineError: if the pipeline file is malformed
    :raises InternalError: if the Analysis/IAP server could not process the request although the user input was correct

    :return: True if successful
    """
    grpc_ip = current_app.config['ANALYSIS_SERVER_IP']
    grpc_port = current_app.config['ANALYSIS_SERVER_GRPC_PORT']

    channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    iap_stub = phenopipe_iap_pb2_grpc.PhenopipeIapStub(channel)
    try:
        response = iap_stub.UploadPipeline(
            phenopipe_iap_pb2.UploadPipelineRequest(file=pipeline.stream.read(), author=username)
        )
        return response.success
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Analysis Service")
        elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise PipelineAlreadyExistsError(e.details(), e.initial_metadata()[0][1])
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise InvalidPipelineError(e.details())
        elif e.code() == grpc.StatusCode.INTERNAL:
            raise InternalError(e.details())
        raise  # TODO other error options? --> internal server error? if list of possible grpc errors is exhausted we don't know what error occured


def delete_pipeline(pipeline_id):
    """
    Deletes the specified pipeline form the Analysis/IAP server

    :param pipeline_id: The id which identifies the pipeline

    :return: True if successful
    """
    grpc_ip = current_app.config['ANALYSIS_SERVER_IP']
    grpc_port = current_app.config['ANALYSIS_SERVER_GRPC_PORT']

    channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    iap_stub = phenopipe_iap_pb2_grpc.PhenopipeIapStub(channel)
    try:
        response = iap_stub.DeletePipeline(
            phenopipe_iap_pb2.DeletePipelineRequest(id=pipeline_id)
        )
        return response.success
    except grpc.RpcError as e:
        # TODO raise meaningful exception to return to user
        print(e.details())
        # raise


def get_iap_pipeline(username, pipeline_id):
    """
    Fetches the IAP Analysis pipeline with the given id by author identified by the username from the Analysis/IAP server

    :param username the username of the pipeline author

    :param pipeline_id the id of the pipeline to fetch

    :raises NotFoundError: if the requested pipeline is not found

    :raises UnavailableError: if the Analysis/IAP service is not reachable

    :return: The fetched pipeline
    """
    grpc_ip = current_app.config['ANALYSIS_SERVER_IP']
    grpc_port = current_app.config['ANALYSIS_SERVER_GRPC_PORT']

    channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    iap_stub = phenopipe_iap_pb2_grpc.PhenopipeIapStub(channel)
    try:
        response = iap_stub.GetPipeline(
            phenopipe_iap_pb2.GetPipelineRequest(id=pipeline_id, author=username)
        )
        return response.pipeline
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise NotFoundError(e.details(), "Pipeline")
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Analysis Service")
        raise  # TODO other error options? --> internal server error? if list of possible grpc errors is exhausted we don't know what error occured


def get_iap_pipelines(username):
    """
    Fetches all available IAP Analysis pipelines from the Analysis/IAP server

    :raises UnavailableError: if the Analysis/IAP service is not reachable

    :return: A list of available pipelines
    """
    grpc_ip = current_app.config['ANALYSIS_SERVER_IP']
    grpc_port = current_app.config['ANALYSIS_SERVER_GRPC_PORT']

    channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    iap_stub = phenopipe_iap_pb2_grpc.PhenopipeIapStub(channel)
    try:
        response = iap_stub.GetPipelines(
            phenopipe_iap_pb2.GetPipelinesRequest(author=username)
        )

        return response.pipelines
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            raise UnavailableError("Analysis Service")
        raise  # TODO other error options? --> internal server error? if list of possible grpc errors is exhausted we don't know what error occured
