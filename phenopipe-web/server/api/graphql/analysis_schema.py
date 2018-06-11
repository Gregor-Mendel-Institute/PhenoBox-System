import graphene
from flask import logging
from flask_jwt_extended import get_jwt_identity
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphql_relay import from_global_id
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager

from server.api.graphql.exceptions import UnknownDataError
from server.api.graphql.pipeline_schema import Pipeline
from server.api.graphql.sample_group_schema import SampleGroup
from server.extensions import db
from server.models import SampleGroupModel, PlantModel, SnapshotModel, TimestampModel
from server.models.analysis_model import AnalysisModel
from server.modules.processing.analysis.analysis import get_iap_pipeline
from server.modules.processing.remote_exceptions import UnavailableError, NotFoundError


class Analysis(SQLAlchemyObjectType):
    class Meta:
        model = AnalysisModel
        interfaces = (Node,)

    sample_groups = SQLAlchemyConnectionField(SampleGroup)
    pipeline = graphene.Field(Pipeline)
    snapshots = graphene.ConnectionField(lambda: Snapshot)

    def resolve_sample_groups(self, args, context, info):
        return db.session.query(SampleGroupModel) \
            .join(PlantModel) \
            .join(SnapshotModel, SnapshotModel.plant_id == PlantModel.id) \
            .join(TimestampModel, SnapshotModel.timestamp_id == TimestampModel.id) \
            .options(
            contains_eager("plants"),
            contains_eager("plants.snapshots")
        ).filter(TimestampModel.analyses.any(AnalysisModel.id == self.id))

    def resolve_pipeline(self, args, context, info):
        try:
            identity = get_jwt_identity()
            pipeline = get_iap_pipeline(identity.get('username'), self.pipeline_id)
            return Pipeline.from_grpc_type(pipeline)
        except NotFoundError as e:
            raise
        except UnavailableError as e:
            raise

    def resolve_snapshots(self, args, context, info):
        return db.session.query(SnapshotModel).filter(SnapshotModel.timestamp_id == self.timestamp_id).all()


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


# noinspection PyPep8
from server.api.graphql.snapshot_schema import Snapshot
# noinspection PyPep8
