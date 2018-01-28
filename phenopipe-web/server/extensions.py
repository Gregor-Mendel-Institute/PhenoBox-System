#
# Database ORM
#
import grpc
from flask_sqlalchemy import SQLAlchemy
from rq import Queue

from server.utils.redis_status_cache.redis_status_cache import StatusCache
from server.utils.util import static_vars

db = SQLAlchemy()

from flask_migrate import Migrate

migrate = Migrate()

import redis
from server.modules.printer import PrintQueue

# TODO access config values
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)
print_queue = PrintQueue(redis_db)

analysis_job_queue = Queue('analysis', connection=redis_db)
postprocessing_job_queue = Queue('postprocessing', connection=redis_db)
analyses_status_cache = StatusCache(redis_db, 'analysis')
postprocessing_status_cache = StatusCache(redis_db, 'postprocessing')


@static_vars(channel=None)
def get_iap_channel():
    if get_iap_channel.channel is None:
        from flask import current_app
        grpc_ip = current_app.config['ANALYSIS_SERVER_IP']
        grpc_port = current_app.config['ANALYSIS_SERVER_GRPC_PORT']
        get_iap_channel.channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    return get_iap_channel.channel


@static_vars(channel=None)
def get_r_channel():
    if get_r_channel.channel is None:
        from flask import current_app
        grpc_ip = current_app.config['POSTPROCESS_SERVER_IP']
        grpc_port = current_app.config['POSTPROCESS_SERVER_GRPC_PORT']
        get_r_channel.channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    return get_r_channel.channel


# cors = CORS(resources={r"/*": {"origins": "*"}})
from flask_jwt_extended import JWTManager

jwt = JWTManager()

# from server.modules.printer import Printer
#
# printer = Printer()
# printer.setDaemon(True)
