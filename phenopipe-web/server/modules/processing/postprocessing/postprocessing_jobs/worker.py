from rq import Connection, Worker
from rq.handlers import move_to_failed_queue

from server.modules.processing.postprocessing.postprocessing_jobs.worker_extensions import get_redis_connection, \
    get_config


def rq_exception_handler(job, exc_type, exc_value, traceback):
    print('Exception')
    print(job)


def run(config_path, config_name):
    get_config(config_path, config_name)
    with Connection(get_redis_connection()):
        worker = Worker(['postprocessing'], exception_handlers=[rq_exception_handler, move_to_failed_queue])
        worker.work()
