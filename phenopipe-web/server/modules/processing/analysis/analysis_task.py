from collections import OrderedDict
from datetime import datetime

import dateutil.parser
from rq import Queue
from rq.job import Job, JobStatus

from server.modules.processing.task_state import TaskState
from server.utils.util import as_string


class AnalysisTask(object):

    def __init__(self, connection, timestamp_id, pipeline_id, rq_queue_name='', name='', description='',
                 import_job=None,
                 analysis_job=None, export_job=None, ):
        self._connection = connection
        self._queue = Queue(rq_queue_name, connection=connection)
        self._timestamp_id = timestamp_id
        self._pipeline_id = pipeline_id
        self._name = name
        self._description = description
        self._jobs = OrderedDict(
            [('import_job', import_job), ('analysis_job', analysis_job), ('export_job', export_job)])
        self._created_at = datetime.utcnow()
        self._message = ''

    @classmethod
    def from_key(cls, connection, key):
        parts = key.split(':', 2)
        task = cls(connection, parts[1], parts[2])
        task.load()
        return task

    @classmethod
    def key_for(cls, timestamp_id, pipeline_id):
        """The Redis key that is used to store task hash under."""
        return b'ana_tasks:' + str(timestamp_id) + ':' + str(pipeline_id)

    @classmethod
    def fetch(cls, connection, timestamp_id, pipeline_id):
        """Fetches a persisted task from its corresponding Redis key and
        instantiates it.
        """
        job = cls(connection, timestamp_id, pipeline_id)
        job.load()
        return job

    @property
    def key(self):
        """The Redis key that is used to store task hash under."""
        return self.key_for(self.timestamp_id, self.pipeline_id)

    def to_dict(self):
        """
        Returns a serialization of the current Task instance

        """
        obj = {'queue_name': self._queue.name,
               'created_at': self._created_at.isoformat(), 'name': self.name,
               'description': self.description, 'message': self.message}
        if self.import_job is not None:
            obj['import_job'] = self.import_job.id
        if self.analysis_job is not None:
            obj['analysis_job'] = self.analysis_job.id
        if self.export_job is not None:
            obj['export_job'] = self.export_job.id
        return obj

    def save(self):
        self._connection.hmset(self.key, self.to_dict())

    def load(self):
        key = self.key
        obj = self._connection.hgetall(key)
        if len(obj) == 0:
            raise ValueError('No such task: {0}'.format(key))

        def to_date(date_str):
            if date_str is None:
                return
            else:
                return dateutil.parser.parse(as_string(date_str))

        self._created_at = to_date(as_string(obj.get('created_at')))
        self.name = as_string(obj.get('name'))
        self.description = as_string(obj.get('description'))
        self.message = as_string(obj.get('message'))
        self._queue = Queue(as_string(obj.get('queue_name')), connection=self._connection)
        import_job_id = as_string(obj.get('import_job', None))
        analysis_job_id = as_string(obj.get('analysis_job', None))
        export_job_id = as_string(obj.get('export_job', None))
        self.import_job = self._queue.fetch_job(import_job_id)
        self.analysis_job = self._queue.fetch_job(analysis_job_id)
        self.export_job = self._queue.fetch_job(export_job_id)

    @property
    def state(self):
        if self.import_job is not None:
            first_state = self.import_job.get_status()
        else:
            first_state = self.analysis_job.get_status()

        if first_state == JobStatus.DEFERRED:
            return TaskState.CREATED
        if first_state == JobStatus.QUEUED:
            return TaskState.QUEUED
        if first_state == JobStatus.STARTED:
            return TaskState.RUNNING
        if first_state == JobStatus.FAILED:
            return TaskState.FAILED
        # first job finished
        if self.analysis_job.status == JobStatus.FINISHED and self.export_job.status == JobStatus.FINISHED:
            return TaskState.FINISHED
        elif self.analysis_job.get_status() == JobStatus.FAILED or self.export_job.status == JobStatus.FAILED:
            return TaskState.FAILED

        return TaskState.RUNNING

    def update_message(self, message):
        self.message = message
        self._connection.hset(self.key, 'message', message)

    def fetch_message(self):
        self.message = self._connection.hget(self.key, 'message')
        return self.message

    @property
    def jobs(self):
        return self._jobs

    @property
    def timestamp_id(self):
        return self._timestamp_id

    @property
    def pipeline_id(self):
        return self._pipeline_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def created_at(self):
        return self._created_at

    @property
    def import_job(self):
        return self._jobs.get('import_job')

    @import_job.setter
    def import_job(self, value):
        if value is None or isinstance(value, Job):
            self._jobs['import_job'] = value
        else:
            raise TypeError('Argument has to be of type "rq.Job".')

    @property
    def analysis_job(self):
        return self._jobs.get('analysis_job')

    @analysis_job.setter
    def analysis_job(self, value):
        if value is None or isinstance(value, Job):
            self._jobs['analysis_job'] = value
        else:
            raise TypeError('Argument has to be of type "rq.Job".')

    @property
    def export_job(self):
        return self._jobs.get('export_job')

    @export_job.setter
    def export_job(self, value):
        if value is None or isinstance(value, Job):
            self._jobs['export_job'] = value
        else:
            raise TypeError('Argument has to be of type "rq.Job".')
