import graphene
from flask import logging
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphql_relay import from_global_id, to_global_id
from sqlalchemy.exc import IntegrityError, DBAPIError

from server.api.graphql.exceptions import UnknownDataError, ConflictingDataError
from server.api.graphql.image_schema import Image
from server.extensions import db
from server.models import SnapshotModel, TimestampModel, PlantModel, ImageModel, AnalysisModel


class Snapshot(SQLAlchemyObjectType):
    class Meta:
        model = SnapshotModel
        interfaces = (Node,)

    images = SQLAlchemyConnectionField(Image, with_type=graphene.String())
    analyses = graphene.ConnectionField(lambda: Analysis)

    def resolve_images(self, args, context, info):
        conds = list()
        query = db.session.query(ImageModel).filter(ImageModel.snapshot_id == self.id)
        if 'with_type' in args:
            conds.append(ImageModel.type == args.get('with_type'))

        for cond in conds:
            query = query.filter(cond)
        return query.all()

    def resolve_analyses(self, args, context, info):
        return db.session.query(AnalysisModel).filter(AnalysisModel.timestamp_id == self.timestamp_id).all()


class SnapshotInput(graphene.InputObjectType):
    timestamp_id = graphene.NonNull(graphene.Int)
    plant_id = graphene.NonNull(graphene.Int)


class ChangeSnapshotExclusion(graphene.Mutation):
    class Input:
        snapshot_id = graphene.NonNull(graphene.ID)
        exclude = graphene.NonNull(graphene.Boolean)

    id = graphene.ID()
    excluded = graphene.Boolean()

    def mutate(self, args, context, info):
        snapshot_id = args.get('snapshot_id')
        _, snapshot_db_id = from_global_id(snapshot_id)
        try:
            snapshot = db.session.query(SnapshotModel).get(snapshot_db_id)
            snapshot.excluded = args.get('exclude')

            db.session.add(snapshot)
            db.session.flush()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        db.session.commit()

        return ChangeSnapshotExclusion(id=snapshot_id, excluded=args.get('exclude'))


class CreateSnapshot(graphene.Mutation):
    class Input:
        plant_id = graphene.NonNull(graphene.ID)
        phenobox_id = graphene.NonNull(graphene.String)
        camera_position = graphene.NonNull(graphene.String)
        measurement_tool = graphene.NonNull(graphene.String)

    id = graphene.ID()
    timestamp_id = graphene.ID()
    new_timestamp = graphene.Boolean()

    def mutate(self, args, context, info):
        plant_id = args.get('plant_id')
        _, plant_db_id = from_global_id(plant_id)
        plant = db.session.query(PlantModel).get(plant_db_id)
        experiment_id = plant.sample_group.experiment_id
        timestamp, created = TimestampModel.get_or_create(experiment_id)
        snapshot = SnapshotModel(plant_id=plant_db_id, timestamp_id=timestamp.id,
                                 camera_position=args.get('camera_position'),
                                 measurement_tool=args.get('measurement_tool'), phenobox_id=args.get('phenobox_id'))

        try:
            db.session.add(snapshot)
            db.session.flush()
        except IntegrityError as err:
            db.session.rollback()
            if err.orig.diag.constraint_name == u'uq_snapshot_plant_id_timestamp_id':
                raise ConflictingDataError('There already exists a snapshot for this plant and timestamp')
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        db.session.commit()

        return CreateSnapshot(id=to_global_id('Snapshot', snapshot.id),
                              timestamp_id=to_global_id('Timestamp', timestamp.id), new_timestamp=created)


class DeleteSnapshot(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, db_id = from_global_id(ql_id)
        snapshot = db.session.query(SnapshotModel).get(db_id)
        if snapshot is None:
            return  # Exception to indicate this entry does not exist
        try:
            snapshot.purge()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteSnapshot(id=ql_id)


# noinspection PyPep8
from server.api.graphql.analysis_schema import Analysis
# noinspection PyPep8
