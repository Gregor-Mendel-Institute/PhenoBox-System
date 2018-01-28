from pickle import loads, dumps

from server.utils.redis_status_cache.status import Status
from server.utils.util import _as_string


class StatusObject(object):
    """
    Class to represent the status of a collection of background jobs
    """
    current_status_key = 'current_status'
    current_message_key = 'current_message'
    name_key = 'name'
    description_key = 'description'
    id_key = 'id'
    # TODO add created_at
    job_ids_key = 'job_ids'

    def __init__(self, name, description, status_id, job_ids=None, current_status=Status.created, current_message=''):
        """
        Initalize a :class:`StatusObject`

        :param name: The name of the job collection/Task
        :param description: A short description of the task
        :param status_id: The unique id of this StatusObject
        :param job_ids: A dict containing all jobs which belong to this StatusObject. Mapping the name of the job to its id
        :param current_status: The latest :class:`.Status` of this task
        :param current_message: The latest status message
        """
        self._name = name
        self._description = description
        self._id = status_id
        if job_ids is None:
            self._job_ids = dict()
        else:
            self._job_ids = job_ids
        self._current_status = current_status
        self._current_message = current_message

    @classmethod
    def load(cls, obj):
        """
        Deserialize the given object to create an instance of :class:`StatusObject`

        :param obj: A serialized version of a :class:`StatusObject`

        :return: instance of the deserialized :class:`StatusObject`
        """
        status_id = _as_string(obj.get(StatusObject.id_key))
        name = _as_string(obj.get(StatusObject.name_key))
        description = _as_string(obj.get(StatusObject.description_key))
        current_status = loads(obj.get(StatusObject.current_status_key)) if obj.get(
            StatusObject.current_status_key) else None
        current_message = _as_string(obj.get(StatusObject.current_message_key))
        job_ids = loads(obj.get(StatusObject.job_ids_key)) if obj.get(StatusObject.job_ids_key) else {}
        return cls(name, description, status_id, job_ids=job_ids, current_status=current_status,
                   current_message=current_message)

    @classmethod
    def load_field(cls, field, field_key):
        """
        Deserialize the given field instead of the full object

        :param field: The serialized content of the field
        :param field_key: The key for the given field

        :return: The deserialized representation of the requested field
        """
        if field_key == StatusObject.id_key or field_key == StatusObject.name_key or field_key == StatusObject.description_key:
            return _as_string(field)
        if field_key == StatusObject.current_status_key:
            return loads(field) if field is not None else None
        if field_key == StatusObject.current_message_key:
            return _as_string(field)
        if field_key == StatusObject.job_ids_key:
            return loads(field) if field is not None else {}

    def serialize(self):
        obj = dict()
        obj[StatusObject.id_key] = self._id
        obj[StatusObject.name_key] = self._name
        obj[StatusObject.description_key] = self._description
        if self._current_status is not None:
            obj[StatusObject.current_status_key] = dumps(self._current_status)
        if self._current_message is not None:
            obj[StatusObject.current_message_key] = self._current_message
        if self._job_ids is not None:
            obj[StatusObject.job_ids_key] = dumps(self._job_ids)
        return obj

    def has_error(self):
        return self._current_status == Status.error

    def get_job_id(self, job_name):
        return self._job_ids.get(job_name)

    def get_job_names(self):
        return self._job_ids.keys()

    def get_job_status(self, job_id):
        # get status from RQ
        pass

    def get_job_name_id_map(self):
        return self._job_ids.items()

    def add_job(self, job_name, job_id):
        self._job_ids[job_name] = job_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def id(self):
        return self._id

    @property
    def current_status(self):
        return self._current_status

    @current_status.setter
    def current_status(self, value):
        self._current_status = value

    @property
    def current_message(self):
        return self._current_message

    @current_message.setter
    def current_message(self, value):
        self._current_message = value
