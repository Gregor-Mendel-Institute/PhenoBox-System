import os
import sys

from rq import Connection, Worker
from rq.handlers import move_to_failed_queue

from server.modules.processing.analysis.analysis_jobs.worker_extensions import get_redis_connection, get_config


# TODO Proper exception handling and logging
def rq_exception_handler(job, exc_type, exc_value, traceback):
    print('Exception')
    print(job)


if __name__ == '__main__':
    get_config('{}/{}'.format(os.path.dirname(sys.argv[0]), '../../../../config/'), sys.argv[1])
    with Connection(get_redis_connection()):
        worker = Worker(['analysis'], exception_handlers=[rq_exception_handler, move_to_failed_queue])
        worker.work()
