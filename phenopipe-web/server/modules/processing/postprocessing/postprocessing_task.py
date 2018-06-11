from collections import OrderedDict
from datetime import datetime

import dateutil.parser
from rq import Queue
from rq.job import Job, JobStatus

from server.modules.processing.task_state import TaskState
from server.utils.util import as_string


class PostprocessingTask(object):

    def __init__(self, connection, analysis_id, postprocessing_stack_id, rq_queue_name='', name='', description='',
                 processing_job=None):
        self._connection = connection
        self._queue = Queue(rq_queue_name, connection=connection)
        self._analysis_id = analysis_id
        self._postprocessing_stack_id = postprocessing_stack_id
        self._name = name
        self._description = description
        self._jobs = OrderedDict([('processing_job', processing_job)])
        self._created_at = datetime.utcnow()
        self._message = ''

    @classmethod
    def from_key(cls, connection, key):
        parts = key.split(':', 2)
        task = cls(connection, parts[1], parts[2])
        # TODO check for existence and raise error?
        task.load()
        return task

    @classmethod
    def key_for(cls, analysis_id, postprocessing_stack_id):
        """The Redis key that is used to store task hash under."""
        return b'post_tasks:' + str(analysis_id) + ':' + str(postprocessing_stack_id)

    @classmethod
    def fetch(cls, connection, analysis_id, postprocessing_stack_id):
        """Fetches a persisted task from its corresponding Redis key and
        instantiates it.
        """
        job = cls(connection, analysis_id, postprocessing_stack_id)
        job.load()
        return job

    @property
    def key(self):
        """The Redis key that is used to store task hash under."""
        return self.key_for(self.analysis_id, self.postprocessing_stack_id)

    def to_dict(self):
        """
        Returns a serialization of the current Task instance

        """
        obj = {'queue_name': self._queue.name, 'created_at': self._created_at.isoformat(), 'name': self.name,
               'description': self.description, 'message': self.message}
        if self.processing_job is not None:
            obj['processing_job'] = self.processing_job.id
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
        processing_job_id = as_string(obj.get('processing_job', None))
        self.processing_job = self._queue.fetch_job(processing_job_id)

    def update_message(self, message):
        self.message = message
        self._connection.hset(self.key, 'message', message)

    def fetch_message(self):
        self.message = self._connection.hget(self.key, 'message')
        return self.message

    @property
    def state(self):
        state = self.processing_job.get_status()
        if state == JobStatus.DEFERRED:
            return TaskState.CREATED
        if state == JobStatus.QUEUED:
            return TaskState.QUEUED
        if state == JobStatus.STARTED:
            return TaskState.RUNNING
        if state == JobStatus.FAILED:
            return TaskState.FAILED
        return TaskState.FINISHED

    @property
    def analysis_id(self):
        return self._analysis_id

    @property
    def postprocessing_stack_id(self):
        return self._postprocessing_stack_id

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
    def jobs(self):
        return self._jobs

    @property
    def processing_job(self):
        return self._jobs.get('processing_job')

    @processing_job.setter
    def processing_job(self, value):
        if value is None or isinstance(value, Job):
            self._jobs['processing_job'] = value
        else:
            raise TypeError('Argument has to be of type "rq.Job".')
