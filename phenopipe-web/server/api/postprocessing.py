import json

from flask import jsonify
from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from graphql_relay import from_global_id
from werkzeug.exceptions import UnsupportedMediaType

from server.api.blueprints import api
from server.extensions import db
from server.gen.phenopipe_r_pb2 import PostprocessingStack, PostprocessingScript
from server.models import AnalysisModel
from server.modules.postprocessing.postprocessing import upload_stack, get_postprocessing_stacks, submit_postprocesses


@api.route('/upload-postprocessing-stack', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def upload_postprocessing_stack():
    # TODO document returns
    """
    API endpoint for uploading the given postprocessing stack to the Postprocessing server

    This request must contain the scripts in the 'files[]' field and the corresponding metadata in the 'fileMeta[]' field.
    The metadata object should contain the 'name' and the 'description' of the corresponding script.
    The order of the files represents the order in which the scripts will be executed in a postprocessing task.
    The form part of the multipart-form request should contain the following fields: 'name', 'description' and 'author'

    """
    if request.mimetype == 'multipart/form-data':
        identity = get_jwt_identity()
        username = identity.get('username')
        meta_list = request.form.getlist('fileMeta[]')
        scripts = []
        for index, entry in enumerate(request.files.getlist('files[]')):
            print(entry.filename)
            print(meta_list[index])

            meta = json.loads(meta_list[index])
            script = PostprocessingScript(name=meta['name'],
                                          description=meta['description'],
                                          index=index,
                                          file=entry.stream.read())
            scripts.append(script)
        stack = PostprocessingStack(name=request.form['name'],
                                    description=request.form['description'],
                                    author=username,
                                    scripts=scripts)
        upload_stack(stack)
        return jsonify({'msg': 'Uploaded stack successfully'}), 201
    else:
        raise UnsupportedMediaType("Media type has to be 'multipart/form-data'")


@api.route('/postprocess_analysis', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def postprocess_analysis():
    # TODO document returns
    """
    API endpoint for starting the postprocessing of an analysis

    The request body must contain the 'analysis_id' and a list 'postprocessing_stack_ids' containing the IDs of the stacks
    which should be applied to the analysis results.

    :return: a dict containing a 'msg', a list of 'postprocess_ids' representing the status IDs of the corresponding tasks
        and a list of postprocessing stack IDs which have already been applied to the given analysis.
    """
    identity = get_jwt_identity()
    parsed_request = request.get_json()
    postprocessing_ids = parsed_request['postprocessing_stack_ids']
    analysis_id = parsed_request['analysis_id']
    note = parsed_request['note'] if 'note' in parsed_request else ''
    if analysis_id is not None:
        ql_type, analysis_db_id = from_global_id(analysis_id)

        analysis = db.session.query(AnalysisModel).get(analysis_db_id)

        if postprocessing_ids is not None:
            result = submit_postprocesses(analysis, postprocessing_ids, note, identity['username'])
            # TODO throw error if one postprocess can't be started
            return jsonify({'msg': 'Started Postprocesses', 'postprocess_ids': result['status_ids'],
                            'already_finished': result['already_finished']}), 202
        return jsonify({'msg': 'No postprocessing stack ids given'}), 422
    else:
        return jsonify({'msg': 'No analysis id given'}), 422


@api.route('/test_r', methods=['GET'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
# @jwt_required
def test_r():
    get_postprocessing_stacks()
    return jsonify({'msg': 'Testing'})
