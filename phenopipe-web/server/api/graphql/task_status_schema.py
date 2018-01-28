import graphene
from enum import Enum
from graphql_relay import to_global_id, from_global_id
from rq import Queue

from server.api.graphql.rq_job_schema import JobConnection, Job
from server.api.graphql.status_log_entry_schema import StatusLogEntry, StatusLogEntryConnection
from server.extensions import redis_db, analyses_status_cache, postprocessing_status_cache
from server.utils.redis_status_cache.status import Status


class TaskType(Enum):
    analysis = 1
    postprocess = 2


class TaskStatus(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    task_type = graphene.Enum.from_enum(TaskType)()
    current_status = graphene.Enum.from_enum(Status)()
    current_message = graphene.String()
    jobs = graphene.ConnectionField(JobConnection)
    log = graphene.ConnectionField(StatusLogEntryConnection, newest_first=graphene.Boolean())

    @classmethod
    def from_status_object(cls, queue_name, type, status_object, status_id):
        queue = Queue(queue_name, connection=redis_db)
        job_list = []
        for job_name, job_id in status_object.get_job_name_id_map():
            job_list.append(Job.from_rq_job_instance(queue.fetch_job(job_id), job_name))

        instance = cls(id=to_global_id('TaskStatus', status_id),
                       name=status_object.name,
                       description=status_object.description,
                       task_type=type,
                       current_status=status_object.current_status,
                       current_message=status_object.current_message,
                       jobs=job_list)
        return instance

    def resolve_current_status(self, args, context, info):
        return self.current_status.value

    def resolve_log(self, args, context, info):
        if self.task_type == TaskType.analysis:
            cache = analyses_status_cache
        else:
            cache = postprocessing_status_cache
        _, status_id = from_global_id(self.id)

        log_entries = []
        if 'newest_first' in args and args.get('newest_first'):
            raw_log_entries = cache.get_full_log(status_id, reverse=True)
        else:
            raw_log_entries = cache.get_full_log(status_id)

        for timestamp, message, progress in raw_log_entries:
            log_entries.append(StatusLogEntry(timestamp=timestamp, message=message, progress=progress))

        return log_entries


class TaskStatusConnection(graphene.Connection):
    class Meta:
        node = TaskStatus
