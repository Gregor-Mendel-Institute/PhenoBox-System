import graphene


class Job(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    status = graphene.String()
    enqueued_at = graphene.String()
    started_at = graphene.String()
    finished_at = graphene.String()

    @classmethod
    def from_rq_job_instance(cls, rq_job, name):
        if rq_job is None:
            instance = cls(name=name)
        else:
            instance = cls(id=rq_job.id, name=name, description=rq_job.description, status=rq_job.get_status(),
                           enqueued_at=rq_job.enqueued_at,
                           started_at=rq_job.started_at, finished_at=rq_job.ended_at)
        return instance


class JobConnection(graphene.Connection):
    class Meta:
        node = Job
