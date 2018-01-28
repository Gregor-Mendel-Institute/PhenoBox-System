import os

import grpc
from flask import current_app
from graphql_relay import to_global_id
from rq.job import Job

from server.extensions import db, analyses_status_cache, analysis_job_queue, redis_db
from server.gen import phenopipe_iap_pb2_grpc, phenopipe_iap_pb2
from server.models.analysis_model import AnalysisModel
from server.modules.analysis.analysis_jobs import invoke_iap_import, invoke_iap_analysis, invoke_iap_export, \
    invoke_postprocesses_after_export
from server.modules.processing.exceptions import AlreadyRunningError, AlreadyFinishedError, InvalidPathError
from server.modules.processing.remote_exceptions import UnavailableError, PipelineAlreadyExistsError, \
    InvalidPipelineError, InternalError, NotFoundError
from server.utils.redis_status_cache.redis_status_cache import StatusCache
from server.utils.redis_status_cache.status import Status
from server.utils.redis_status_cache.status_object import StatusObject
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


def _submit_full(analysis_id, status_name, status_description, analysis_status_id, timestamp, experiment_name,
                 coordinator, scientist,
                 input_path,
                 output_path,
                 local_path,
                 pipeline_id,
                 username):
    """
    Submits all background jobs that are necessary to analyze timestamp data.

    If the image data of timestamp are not yet imported to IAP this will be done first.
    After that the actual analysis will be executed and then the data will be exported from IAP to the given output_path

    :param analysis_id: The ID of the :class:`~server.models.analysis_model.AnalysisModel`
    :param status_name: The name of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param status_description: The description of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param analysis_status_id: The ID of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param timestamp: The timestamp which should be analyzed
    :param experiment_name: The name of the experiment the timestamp belongs to
    :param coordinator: The name of the experiment coordinator
    :param scientist: The name of the scientist conducting this experiment
    :param input_path: The path, as SMB URL, where the input data (images) are stored
    :param output_path: The path, as SMB URL, where the exported data should be stored
    :param local_path: The path to the data on the local system (input path translated to local mount point)
    :param pipeline_id: The id of the IAP Pipeline which should be used for analysis
    :param username: The username of the User requesting this process

    :raises AlreadyRunningError: if there are already jobs running for the given parameters

    :return: A dictionary containing the 'status_id' and a list of RQ Job instances ('jobs')
    """
    status = StatusObject(status_name, status_description, analysis_status_id, current_status=Status.pending)
    can_run = analyses_status_cache.checked_put(username, status)
    if can_run:
        import_job = None
        if timestamp.iap_exp_id is None:
            import_job = Job.create(invoke_iap_import, (timestamp.id, experiment_name,
                                                        coordinator,
                                                        scientist,
                                                        local_path, input_path, username, analysis_status_id),
                                    connection=redis_db,
                                    result_ttl=-1,
                                    ttl=-1,
                                    timeout=_timeout_import,
                                    origin=analysis_job_queue.name,
                                    description='Import Image data of experiment "{}" at timestamp {} to IAP'.format(
                                        experiment_name,
                                        to_global_id('Timestamp', timestamp.id)))
        # TODO use pipeline name in description
        analysis_job = Job.create(invoke_iap_analysis, (analysis_id, timestamp.id,
                                                        username, analysis_status_id,
                                                        timestamp.iap_exp_id),
                                  connection=redis_db,
                                  result_ttl=-1,
                                  ttl=-1,
                                  timeout=_timeout_analysis,
                                  origin=analysis_job_queue.name,
                                  description='Analyse the data of timestamp {} with the pipeline "{}" in IAP'.format(
                                      to_global_id('Timestamp', timestamp.id), pipeline_id),
                                  depends_on=import_job)
        shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
        export_job = Job.create(invoke_iap_export,
                                (timestamp.id, output_path, username, analysis_status_id, shared_folder_map),
                                connection=redis_db,
                                result_ttl=-1,
                                ttl=-1,
                                timeout=_timeout_export,
                                origin=analysis_job_queue.name,
                                description='Export the IAP results for timestamp {} to "{}"'.format(
                                    to_global_id('Timestamp', timestamp.id), output_path),
                                depends_on=analysis_job)

        if import_job is not None:
            status.add_job('import', import_job.id)
        status.add_job('analysis', analysis_job.id)
        status.add_job('export', export_job.id)

        try:
            analyses_status_cache.update(username, status)
        except KeyError:
            pass  # Cannot happen because of the checked put in the beginning

        export_job.register_dependency()
        export_job.save()
        if import_job is not None:
            analysis_job.register_dependency()
            analysis_job.save()
            analysis_job_queue.enqueue_job(import_job)
        else:
            analysis_job_queue.enqueue_job(analysis_job)
        return {'status_id': analysis_status_id, 'jobs': [import_job, analysis_job, export_job]}

    else:
        # Currently in progress
        raise AlreadyRunningError(username, analysis_status_id,
                                  'The requested analysis is currently in progress')


def _submit_export_only(status_name, status_description, analysis_status_id, analysis, timestamp, output_path,
                        username):
    """
    Only exports the analysis results from IAP.

    :param status_name: The name of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param status_description: The description of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param analysis_status_id: The ID of the :class:`~server.utils.redis_status_cache.status_object.StatusObject`
    :param analysis: The analysis for which the data should be exported
    :param timestamp: The timestamp the analysis belongs to
    :param output_path: The path, as SMB URL, were the exported results should be stored
    :param username: The username of the user issuing this request

    :raises AlreadyRunningError: if there are already jobs running for the given parameters

    :return:A dictionary containing the 'status_id' and a list of RQ Job instances ('jobs')
    """
    status = StatusObject(status_name, status_description, analysis_status_id, current_status=Status.pending)
    can_run = analyses_status_cache.checked_put(username,
                                                status)
    if can_run:
        shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
        export_job = Job.create(invoke_iap_export,
                                (timestamp.id, output_path, username, analysis_status_id, shared_folder_map,
                                 analysis.iap_id),
                                connection=redis_db,
                                result_ttl=-1,
                                ttl=-1,
                                timeout=_timeout_export,
                                description='Export the IAP results for timestamp {} to "{}"'.format(
                                    to_global_id('Timestamp', timestamp.id), output_path))
        status.add_job('export', export_job.get_id())
        try:
            analyses_status_cache.update(username, status)
        except KeyError:
            pass  # This can not happen because we do the checked put first
        analysis_job_queue.enqueue_job(export_job)
        return {'status_id': analysis_status_id, 'jobs': [None, None, export_job]}
    else:
        # Currently in progress

        raise AlreadyRunningError(username, analysis_status_id,
                                  'The requested analysis is currently in progress')


def is_job_running_for(timestamp_id):
    """
    Checks if there is currently a postprocess running for the given analysis

    :param timestamp_id: The ID of the timestamp to look up

    :return: True if there is a job which processes the given timestamp. False otherwise.
    """
    identifiers = analyses_status_cache.get_all_identifiers()
    for identifier in identifiers:
        if is_job_running_for_user(identifier, timestamp_id):
            return True
    return False


def is_job_running_for_user(username, timestamp_id):
    """
    Checks if there is currently an analysis running for the given timestamp which has been issued by the given user

    :param username: The username of the User who has started the analysis job
    :param timestamp_id: The ID of the timestamp to look up

    :return: True if there is a job from the given user which processes the given timestamp. False otherwise
    """
    status_list = analyses_status_cache.get_all(username)
    for status_id in status_list:
        status_key_info = StatusCache.from_id(status_id)
        # Key format for analysis status '[timestamp_id]:[pipeline_id]
        if status_key_info[0] == timestamp_id:
            # There exists a job which currently imports or analyses this snapshot
            return True
    return False


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

    :raises AlreadyRunningError: If the analysis has already been processed.
    :raises AlreadyFinishedError: If the analysis is currently in progress

    :return: A dictionary containing the 'status_id' and a list of RQ Job instances ('jobs')
    """
    shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
    smb_url, local_path = next(((smb, path) for smb, path in shared_folder_map.items() if input_path.startswith(smb)),
                               (None, None))
    if local_path is not None:
        local_path = os.path.join(local_path, remove_prefix(input_path, smb_url))

        analysis_status_id = StatusCache.generate_id(str(timestamp.id), pipeline_id)
        analysis, created = AnalysisModel.get_or_create(timestamp.id, pipeline_id)
        timestamp_start = timestamp.created_at
        if created:
            analysis.snapshots = timestamp.snapshots
            status_name = 'Analyse timestamp data with IAP'
            #TODO use pipeline name
            status_description = 'Full IAP Analysis for experiment "{}" at timestamp(Date:{}) with pipeline "{}".'.format(
                experiment_name,
                timestamp_start.strftime("%a %b %d %H:%M:%S UTC %Y"), pipeline_id)
            try:
                db.session.commit()
                return _submit_full(analysis.id, status_name, status_description, analysis_status_id, timestamp,
                                    experiment_name,
                                    coordinator, scientist,
                                    input_path,
                                    output_path,
                                    local_path,
                                    pipeline_id, username)
            except AlreadyRunningError as e:  # TODO evaluate: should not happen because of the get_or_create implementation
                db.session.delete(analysis)
                db.session.commit()
                raise
        else:
            if analysis.export_path is None:
                # This analysis has already been processed
                status_name = 'IAP Export'
                # TODO use pipeline name
                status_description = 'Only Export IAP Analysis results for experiment "{}" at timestamp({}) with pipeline "{}".'.format(
                    experiment_name,
                    timestamp_start.strftime("%a %b %d %H:%M:%S UTC %Y"), pipeline_id)
                try:
                    return _submit_export_only(status_name, status_description, analysis_status_id, analysis, timestamp,
                                               output_path,
                                               username)
                except AlreadyRunningError as e:
                    db.session.rollback()
                    raise
            else:
                # Not exactly. actually it could be still running
                # TODO Check for the finished at column to determine if it is still running or not
                raise AlreadyFinishedError(AnalysisModel, analysis.id,
                                           'The requested analysis has already been processed')
    else:
        raise InvalidPathError(input_path, 'The given input path "{}" is not valid'.format(input_path))


def submit_postprocesses_after_export(postprocessing_stack_ids, note, username, export_job):
    """
    Enqueues :meth:`~server.modules.analysis.analysis_jobs.invoke_postprocesses_after_export` to start the postprocessing
    right after the export of the analysis results has finished

    :param postprocessing_stack_ids: A List of postprocessing stack IDs which identify the stacks to be applied to the results
    :param note: A note from the user to make it easier to identify postprocesses
    :param username: The username of the user making this request
    :param export_job: The instance of the RQ export job which this job depends on

    :return: the instance of the enqueued RQ job
    """
    #TODO create jobs and status objects for postprocesses so that tasks immediately show up in the task status view
    #TODO save excluded snapshots right away because otherwise they may change while IAP analysis is running!!
    postprocess_invoke_job = invoke_postprocesses_after_export.delay(postprocessing_stack_ids, note,
                                                                     username, depends_on=export_job)
    return postprocess_invoke_job


def upload_pipeline(pipeline,username):
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
            phenopipe_iap_pb2.UploadPipelineRequest(file=pipeline.stream.read(),author=username)
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
        print(e._state.details)
        # raise


def get_iap_pipeline(username, pipeline_id):
    """
    Fetches the IAP Analysis pipeline with the given id by author identified by the username from the Analysis/IAP server

    :param username the username of the pipeline author

    :param id the id of the pipeline to fetch

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
