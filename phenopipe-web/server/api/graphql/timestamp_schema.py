import graphene
from flask import logging
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id
from sqlalchemy.exc import DBAPIError

from server.api.graphql.exceptions import UnknownDataError
from server.extensions import db
from server.models import TimestampModel


class Timestamp(SQLAlchemyObjectType):
    class Meta:
        model = TimestampModel
        interfaces = (Node,)


class TimestampInput(graphene.InputObjectType):
    experiment_id = graphene.NonNull(graphene.Int)


class CompleteTimestamp(graphene.Mutation):
    class Input:
        timestamp_id = graphene.NonNull(graphene.ID)

    id = graphene.ID()

    def mutate(self, args, context, info):
        try:
            timestamp_id = args.get('timestamp_id')
            _, timestamp_db_id = from_global_id(timestamp_id)
            timestamp = db.session.query(TimestampModel).get(timestamp_db_id)
            setattr(timestamp, 'completed', True)
            db.session.flush()
            db.session.commit()
            return CompleteTimestamp(id=timestamp_id)
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")


class DeleteTimestamp(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(TimestampModel).get(id))
            db.session.commit()
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteTimestamp(id=ql_id)
