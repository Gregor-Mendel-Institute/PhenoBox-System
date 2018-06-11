import graphene
from flask import logging
from flask_jwt_extended import get_jwt_identity
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphql_relay import from_global_id
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager

from server.api.graphql.exceptions import UnknownDataError
from server.api.graphql.postprocessing_stack_schema import PostprocessingStack
from server.api.graphql.sample_group_schema import SampleGroup
from server.extensions import db
from server.models import SampleGroupModel, PlantModel, SnapshotModel
from server.models.postprocess_model import PostprocessModel
from server.modules.processing.postprocessing.postprocessing import get_postprocessing_stack
from server.modules.processing.remote_exceptions import UnavailableError


class Postprocess(SQLAlchemyObjectType):
    class Meta:
        model = PostprocessModel
        interfaces = (Node,)

    sample_groups = SQLAlchemyConnectionField(SampleGroup)
    postprocessing_stack = graphene.Field(PostprocessingStack)

    def resolve_sample_groups(self, args, context, info):
        return db.session.query(SampleGroupModel) \
            .join(PlantModel) \
            .join(SnapshotModel,
                  and_(
                      SnapshotModel.plant_id == PlantModel.id,
                      SnapshotModel.postprocesses.any(PostprocessModel.id == self.id)
                  )) \
            .options(
            contains_eager("plants"),
            contains_eager("plants.snapshots"),
        ).all()

    def resolve_postprocessing_stack(self, args, context, info):
        try:
            identity = get_jwt_identity()
            stack = get_postprocessing_stack(identity.get('username'), self.postprocessing_stack_id)
            return PostprocessingStack.from_grpc_type(stack)
        except UnavailableError as e:
            raise


class DeletePostprocess(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(PostprocessModel).get(id))
            db.session.commit()
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeletePostprocess(id=ql_id)
