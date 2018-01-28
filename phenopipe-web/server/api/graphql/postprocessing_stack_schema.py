import graphene


class PostprocessingScript(graphene.ObjectType):
    id = graphene.String()  # TODO use graphene ID
    name = graphene.String()
    index = graphene.Int()
    description = graphene.String()

    @classmethod
    def from_grpc_type(cls, grpc_script_instance):
        instance = cls(id=grpc_script_instance.id, name=grpc_script_instance.name, index=grpc_script_instance.index,
                       description=grpc_script_instance.description)
        return instance


class PostprocessingScriptConnection(graphene.Connection):
    class Meta:
        node = PostprocessingScript


class PostprocessingStack(graphene.ObjectType):
    id = graphene.String()  # TODO use graphene ID
    name = graphene.String()
    description = graphene.String()
    scripts = graphene.ConnectionField(PostprocessingScriptConnection)

    @classmethod
    def from_grpc_type(cls, grpc_stack_instance):
        scripts = []
        for grpc_script_instance in grpc_stack_instance.scripts:
            scripts.append(
                PostprocessingScript.from_grpc_type(grpc_script_instance))

        instance = cls(id=grpc_stack_instance.id, name=grpc_stack_instance.name,
                       description=grpc_stack_instance.description, scripts=scripts)

        return instance


class PostprocessingStackConnection(graphene.Connection):
    class Meta:
        node = PostprocessingStack
