import logging
import socket
import threading
import time

from flask import current_app

from server.extensions import print_queue, redis_db
from server.utils import Empty

print_cmd = """^R375
^L
AD,24,48,2,2,0,0,{initial1}
AD,24,144,2,2,0,0,{initial2}
W108,24,5,2,Q,8,9,{length},0
{code}
AD,0,280,2,2,0,0,{name}
E
"""


class Printer(threading.Thread):
    """
    Class to represent a thread for handling communication with the label printer. It uses a redis queue to fetch jobs.
    """
    # TODO don't use a static var move to init
    _socket = None

    def __init__(self, ip, port):
        super(Printer, self).__init__()
        self._stop = threading.Event()
        self._ip = ip
        self._port = port
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def set_target(self, ip, port):
        """
        Sets the ip and port of the label printer to connect to

        :param ip: The ip address of the printer
        :param port: The port of the printer

        :return: None
        """
        if self._ip is None and self._port is None:
            self._ip = ip
            self._port = port

    def stop(self):
        """
        Triggers a threading event to signal this thread to stop and terminate cleanly

        :return: None
        """
        self._stop.set()

    def stopped(self):
        """
        :return: A boolean to indicate whether the thread should be stopped or not
        """
        return self._stop.isSet()

    def run(self):
        """
        The main loop of the print thread.

        It takes new jobs from the queue and creates the print commands which should be sent to the printer.
        If there are no print jobs available the connection to the printer is disconnected until jobs are available again.

        """
        print 'starting print worker'
        self._logger.info('Starting Print Worker')
        connected = False
        while not self.stopped():
            try:
                # TODO set status messages in redis
                print_job = print_queue.dequeue_job(block=True, timeout=5)
                if not connected:
                    self._connect()
                    connected = True
                res = self._send_cmd(print_job.get_print_command())
                if res == 1:
                    # redis_db.hset(redis_jobstatus_key, 'status', 'error while sending request')
                    print_queue.requeue_job(print_job)
                    connected = False
                else:
                    pass
                    # redis_db.hset(redis_jobstatus_key, 'status', 'sent to printer')
            except Empty:
                self._disconnect()
                connected = False
            except socket.error as e:
                connected = False
                self._logger.exception('Unable to connect to printer. Reason: ', {e.message})
                print 'socket error'
                # reinsert into queue as next job
                if print_job is not None:
                    print_queue.requeue(print_job)
                # redis_db.hset(job['scientist'] + ':' + job['group_id'], 'status', 'unable to connect to printer')
                # redis_db.expire(job['scientist'] + ':' + job['group_id'], 900)
                # redis_db.expire(job['scientist'] + ':printjobs', 900)
                time.sleep(5)
                # job_json = None
                # try:
                #    job_json = print_queue.dequeue(block=True, timeout=5)
                #    job = json.loads(job_json)
                #    redis_jobstatus_key = job['scientist'] + ':' + job['group_id']
                #    print len(job['plant_ids'])
                #    for plant_name, plant_index, plant_id in job['plant_ids']:
                #        print 'name: ', plant_name, ' id: ', plant_id
                #
                #        self._connect()
                #        name = '{}_{}'.format(job['group_name'], plant_index)
                #        if plant_name.strip() != '':
                #            name += '_{}'.format(plant_name)
                #
                #        res = self._print_code(code=str(plant_id), name=str(name),
                #                               scientist=str(job['scientist']))
                #
                #        if res == 1:
                #            redis_db.hset(redis_jobstatus_key, 'status', 'error while sending request')
                #            break
                #        else:
                #            redis_db.hset(redis_jobstatus_key, 'status', 'sent to printer')
                #    redis_db.expire(redis_jobstatus_key, 900)
                #    redis_db.expire(job['scientist'] + ':printjobs', 900)
                #    job_json = None
        #
        #            except Empty:
        #                self._disconnect()
        #    except socket.error as e:
        #    self._logger.exception('Unable to connect to printer. Reason: ', {e.message})
        #    print 'socket error'
        #    # reinsert into queue as next job
        #    if job_json is not None:
        #        print_queue.requeue(job_json)
        #    redis_db.hset(job['scientist'] + ':' + job['group_id'], 'status', 'unable to connect to printer')
        #    redis_db.expire(job['scientist'] + ':' + job['group_id'], 900)
        #    redis_db.expire(job['scientist'] + ':printjobs', 900)
        #    time.sleep(5)


        self._disconnect()
        print 'print worker stopped'

    @staticmethod
    def _compute_initials(name):
        parts = name.split(' ')
        if len(parts) == 1:
            return name[0], ' '
        else:
            return parts[0][0], parts[len(parts) - 1][0]

    def _connect(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
        try:
            self._socket.connect((self._ip, self._port))
        except socket.error as e:
            if e.errno == 56 and not current_app.config['PRODUCTION']:
                pass
            elif e.errno == 106 and current_app.config['PRODUCTION']:  # TODO Already connected (106 on CentOS 7)
                pass
            else:
                raise  # TODO Notify client or admin?

    def _send_cmd(self, cmd):
        res = self._socket.sendall(cmd)
        if res is not None:
            self._logger.warning('Sending print command to printer failed')
            return 1  # TODO raise exception
        return 0

    def _print_code(self, code, name, scientist):
        initial1, initial2 = Printer._compute_initials(scientist)
        res = self._socket.sendall(
            print_cmd.format(initial1=initial1, initial2=initial2, code=code, name=name, length=len(code)).encode(
                'utf-8'))

        if res is not None:
            self._logger.warning('Sending print command to printer failed')
            print 'sending failed'
            return 1  # TODO raise exception
        return 0

    def _disconnect(self):
        if self._socket is not None:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self._socket = None
