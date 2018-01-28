from flask import jsonify
from graphql_relay import to_global_id

from server.api.blueprints import api
from server.api.graphql.analysis_schema import Analysis
from server.models import AnalysisModel
from server.modules.processing.exceptions import AlreadyRunningError, AlreadyFinishedError, InvalidPathError, \
    AnalysisDataNotPresentError
from server.modules.processing.remote_exceptions import PipelineAlreadyExistsError, UnavailableError, \
    InvalidPipelineError, InternalError, PostprocessingStackAlreadyExistsError


@api.errorhandler(PipelineAlreadyExistsError)
def handle_pipeline_exists(err):
    return jsonify({'msg': err.message, 'pipeline_name': err.name}), 409


@api.errorhandler(UnavailableError)
def handle_unavailable(err):
    return jsonify({'msg': err.message}), 503


@api.errorhandler(InvalidPipelineError)
def handle_invalid_pipeline(err):
    jsonify({'msg': err.message}), 422


@api.errorhandler(InternalError)
def handle_internal_error(err):
    return jsonify({'msg': err.message}), 500


@api.errorhandler(PostprocessingStackAlreadyExistsError)
def handle_postprocessing_stack_exists(err):
    return jsonify({'msg': err.message, 'postprocessing_stack_name': err.name, 'postprocessing_stack_id': err.id}), 409


@api.errorhandler(AlreadyRunningError)
def handle_already_running(err):
    return jsonify({'msg': err.message, 'analysis_status_id': err.status_id}), 409


@api.errorhandler(AlreadyFinishedError)
def handle_already_finished(err):
    return jsonify({'msg': err.message, 'id': to_global_id(err.schema_name, err.db_id)}), 409


@api.errorhandler(InvalidPathError)
def handle_invalid_path(err):
    return jsonify({'msg': err.message}), 422


@api.errorhandler(AnalysisDataNotPresentError)
def handle_analysis_data_not_present(err):
    return jsonify(
        {'msg': err.message, 'analysis_id': to_global_id('Analysis', err.analysis_db_id)}), 412
