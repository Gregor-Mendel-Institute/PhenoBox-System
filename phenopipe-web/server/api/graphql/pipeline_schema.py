import graphene
from graphene import Connection
from graphql_relay import to_global_id


class Pipeline(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()

    @classmethod
    def from_grpc_type(cls, grpc_pipeline_instance):
        ql_id = to_global_id("Pipeline", grpc_pipeline_instance.id)
        instance = cls(id=ql_id, name=grpc_pipeline_instance.name, description=grpc_pipeline_instance.description)
        return instance


class PipelineConnection(Connection):
    class Meta:
        node = Pipeline
