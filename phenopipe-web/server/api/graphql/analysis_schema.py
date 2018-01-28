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
from server.api.graphql.pipeline_schema import Pipeline
from server.api.graphql.sample_group_schema import SampleGroup
from server.extensions import db
from server.models import SampleGroupModel, PlantModel, SnapshotModel
from server.models.analysis_model import AnalysisModel
from server.modules.analysis.analysis import get_iap_pipeline
from server.modules.processing.remote_exceptions import UnavailableError, NotFoundError


class Analysis(SQLAlchemyObjectType):
    class Meta:
        model = AnalysisModel
        interfaces = (Node,)

    sample_groups = SQLAlchemyConnectionField(SampleGroup)
    pipeline = graphene.Field(Pipeline)

    def resolve_sample_groups(self, args, context, info):
        return db.session.query(SampleGroupModel) \
            .join(PlantModel) \
            .join(SnapshotModel,
                  and_(
                      SnapshotModel.plant_id == PlantModel.id,
                      SnapshotModel.analyses.any(AnalysisModel.id == self.id)
                  )) \
            .options(
            contains_eager("plants"),
            contains_eager("plants.snapshots"),
        ).all()

    def resolve_pipeline(self, args, context, info):
        try:
            identity = get_jwt_identity()
            pipeline = get_iap_pipeline(identity.get('username'), self.pipeline_id)
            return Pipeline.from_grpc_type(pipeline)
        except NotFoundError as e:
            raise
        except UnavailableError as e:
            raise


class DeleteAnalysis(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(AnalysisModel).get(id))
            db.session.commit()
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteAnalysis(id=ql_id)
