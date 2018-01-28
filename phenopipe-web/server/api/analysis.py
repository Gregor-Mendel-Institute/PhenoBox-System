import datetime

from flask import jsonify
from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from graphql_relay import from_global_id
from werkzeug.exceptions import UnsupportedMediaType

from server.api.blueprints import api
from server.api.graphql.timestamp_schema import Timestamp
from server.extensions import db
from server.models import ImageModel, SnapshotModel
from server.modules.analysis import submit_iap_jobs
from server.modules.analysis.analysis import submit_postprocesses_after_export, upload_pipeline


@api.route('/analyse-timestamp-data-iap', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def analyse_timestamp_data_iap():
    # TODO document returns
    """
    API endpoint for starting an IAP analysis for the given timestamp.

    The request must contain a 'pipeline_name' and a 'timestamp_id'. Optionally it may contain a list 'postprocessing_stack_ids'
    which contains the IDs of all postprocessing stacks which should be run on the results of the analysis and a 'note'
    to assign to all the postprocesses

    """
    identity = get_jwt_identity()
    parsed_request = request.get_json()
    _,pipeline_id = from_global_id(parsed_request['pipeline_id'])
    postprocessing_ids = parsed_request[
        'postprocessing_stack_ids'] if 'postprocessing_stack_ids' in parsed_request else []
    note = parsed_request['note'] if 'note' in parsed_request else None
    # scientist = identity['name'] + ' ' + identity['surname']

    ql_type, db_id = from_global_id(parsed_request['timestamp_id'])
    timestamp = Timestamp.get_node(db_id, {'session': db.session}, None)
    img = db.session.query(ImageModel).join(SnapshotModel).filter(
        SnapshotModel.timestamp_id == timestamp.id).filter(ImageModel.type == 'raw').first()
    if pipeline_id is not None:
        # TODO pass full name as scientist name instead of username
        ret = submit_iap_jobs(timestamp, timestamp.experiment.name, timestamp.experiment.scientist,
                              timestamp.experiment.scientist,
                              img.path, img.path, pipeline_id, identity['username'])
        if len(postprocessing_ids) > 0:
            submit_postprocesses_after_export(postprocessing_ids, note, identity['username'], export_job=ret['jobs'][2])
            # TODO return postprocessing status ids too
        return jsonify({'msg': 'Started analysis', 'analysis_status_id': ret['status_id']}), 202


@api.route('/upload-iap-pipeline', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def upload_iap_pipeline():
    # TODO document returns
    """
    API endpoint for uploading the given IAP analysis pipeline to the Analyis/IAP server

    This request must contain the pipeline in the 'files[]' field.

    """

    if request.mimetype == 'multipart/form-data':
        identity = get_jwt_identity()
        pipeline = request.files.getlist('files[]')[0]
        upload_pipeline(pipeline, identity.get('username'))
        return jsonify({'msg': 'Uploaded Pipeline Successfully'}), 201
    else:
        raise UnsupportedMediaType("Media type has to be 'multipart/form-data'")


@api.route('/delete-iap-pipeline', methods=['GET', 'POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
# @jwt_required
def delete_iap_pipeline():
    return jsonify({}), 501
    # r = request
    # print(r)
    # pipeline_name = request.get_json()['pipeline_name']
    # success = delete_pipeline(pipeline_name)
    ## TODO check return value/catch errors
    # return jsonify({'msg': 'Deleted Pipeline Successfully'})


@api.route('/testing', methods=['GET'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
# @jwt_required
def test():
    dbtime = db.func.timezone('UTC', db.func.current_timestamp())
    dattime = datetime.datetime.utcnow()
    return jsonify({'msg': 'Testing'})
