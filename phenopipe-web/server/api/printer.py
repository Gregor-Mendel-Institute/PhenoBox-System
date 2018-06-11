from flask import jsonify
from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from graphql_relay import from_global_id, to_global_id

from server.api.blueprints import api
from server.api.graphql.sample_group_schema import SampleGroup
from server.extensions import db, print_queue
from server.modules.printer import PrintJobBundle, PrintJob


@api.route('/print', methods=['POST'])
# @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@jwt_required
def print_group():
    identity = get_jwt_identity()
    ql_id = request.get_json()['id']
    scientist = identity['name'] + ' ' + identity['surname']

    ql_type, db_id = from_global_id(ql_id)
    # TODO query like everywhere else
    group = SampleGroup.get_node(db_id, {'session': db.session}, None)

    if len(group.plants) > 0:
        print_bundle = PrintJobBundle(identity['username'])
        for plant in group.plants:
            plant_id = to_global_id('Plant', plant.id)
            print_bundle.add_job(PrintJob(plant_id, scientist, group.name, plant.full_name))
        print_queue.enqueue(print_bundle)
        # redis_jobstatus_key = scientist + ':' + ql_id
        # redis_db.lpush(scientist + ':printjobs', scientist + ':' + ql_id)
        # redis_db.hmset(redis_jobstatus_key, {
        #    'status': 'queued',
        #    'group_id': ql_id
        # })
        return jsonify({'msg': 'Added print jobs'})
    return jsonify({'msg': 'No Plants to print'})
