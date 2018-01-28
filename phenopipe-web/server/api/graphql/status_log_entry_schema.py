import uuid

import graphene
from graphql_relay import to_global_id


class StatusLogEntry(graphene.ObjectType):
    id = graphene.ID()
    timestamp = graphene.String()
    message = graphene.String()
    progress = graphene.Int()

    def __init__(self, timestamp, message, progress):
        super(StatusLogEntry, self).__init__(id=to_global_id('StatusLogEntry', uuid.uuid4()), timestamp=timestamp,
                                             message=message,
                                             progress=progress)


class StatusLogEntryConnection(graphene.Connection):
    class Meta:
        node = StatusLogEntry

    total_count = graphene.NonNull(graphene.Int)

    def resolve_total_count(self, args, context, info):
        return len(self.iterable)
