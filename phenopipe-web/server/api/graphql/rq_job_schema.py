import graphene
from graphql_relay import to_global_id, from_global_id

from server.api.graphql.status_log_entry_schema import StatusLogEntryConnection, StatusLogEntry
from server.extensions import log_store


class Job(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    status = graphene.String()
    enqueued_at = graphene.String()
    started_at = graphene.String()
    finished_at = graphene.String()
    log = graphene.ConnectionField(StatusLogEntryConnection, newest_first=graphene.Boolean())

    @classmethod
    def from_rq_job_instance(cls, rq_job):
        if rq_job is not None:
            return cls(id=to_global_id('Job', rq_job.id), name=rq_job.meta['name'], description=rq_job.description,
                       status=rq_job.get_status(),
                       enqueued_at=rq_job.enqueued_at,
                       started_at=rq_job.started_at, finished_at=rq_job.ended_at)
        return None

    def resolve_log(self, args, context, info):
        _, job_id = from_global_id(self.id)
        log_entries = []
        if 'newest_first' in args and args.get('newest_first'):
            raw_log_entries = log_store.get_all(job_id, reverse=True)
        else:
            raw_log_entries = log_store.get_all(job_id)

        for timestamp, message, progress in raw_log_entries:
            log_entries.append(StatusLogEntry(timestamp=timestamp, message=message, progress=progress))

        return log_entries


class JobConnection(graphene.Connection):
    class Meta:
        node = Job
