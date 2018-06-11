import graphene
from enum import Enum
from graphql_relay import to_global_id

from server.api.graphql.rq_job_schema import JobConnection, Job
from server.modules.processing.analysis.analysis_task import AnalysisTask
from server.modules.processing.task_state import TaskState


class TaskType(Enum):
    ANALYSIS = 1
    POSTPROCESS = 2

    def __str__(self):
        return self.name

    @property
    def type(self):
        return self.value


class Task(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    # TODO check why tasktype is always null in grapqhl responses
    task_type = graphene.Enum.from_enum(TaskType)()
    current_status = graphene.Enum.from_enum(TaskState)()
    current_message = graphene.String()
    jobs = graphene.ConnectionField(JobConnection)

    # TODO add reference id? (Analysis --> Timestamp ID, Postprocess --> Analysis ID)

    @classmethod
    def from_task_object(cls, task):
        job_list = []
        for job_name in task.jobs:
            job_inst = task.jobs[job_name]
            if job_inst is not None:
                job_list.append(Job.from_rq_job_instance(job_inst))
        if isinstance(task, AnalysisTask):
            type = TaskType.ANALYSIS
        else:
            type = TaskType.POSTPROCESS

        instance = cls(id=to_global_id('Task', task.key),
                       name=task.name,
                       description=task.description,
                       task_type=type,
                       current_status=task.state,
                       current_message=task.fetch_message(),
                       jobs=job_list)
        return instance

    def resolve_current_status(self, args, context, info):
        return self.current_status.value


class TaskConnection(graphene.Connection):
    class Meta:
        node = Task
