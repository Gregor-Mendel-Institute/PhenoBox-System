import graphene
from flask import logging
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id, to_global_id
from sqlalchemy.exc import IntegrityError, DBAPIError

from server.api.graphql.exceptions import UnknownDataError, ConflictingDataError
from server.extensions import db
from server.models import ImageModel


class Image(SQLAlchemyObjectType):
    class Meta:
        model = ImageModel
        interfaces = (Node,)


class ImageInput(graphene.InputObjectType):
    timestamp_id = graphene.NonNull(graphene.Int)
    plant_id = graphene.NonNull(graphene.Int)


class AddImage(graphene.Mutation):
    class Input:
        snapshot_id = graphene.NonNull(graphene.ID)
        path = graphene.NonNull(graphene.String)
        filename = graphene.NonNull(graphene.String)
        angle = graphene.NonNull(graphene.Int)
        type = graphene.String()

    id = graphene.ID()

    def mutate(self, args, context, info):
        snapshot_id = args.get('snapshot_id')
        _, snapshot_db_id = from_global_id(snapshot_id)
        t = args.get('type')
        if t is not None and t.strip() == '':
            t = None
        image = ImageModel(snapshot_id=snapshot_db_id, path=args.get('path'), filename=args.get('filename'),
                           angle=args.get('angle'),
                           image_type=t)

        try:
            db.session.add(image)
            db.session.flush()
        except IntegrityError as err:
            print(err.message)
            db.session.rollback()
            raise ConflictingDataError("Image already exists")
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        db.session.commit()

        return AddImage(id=to_global_id('Image', image.id))


class DeleteImage(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(ImageModel).get(id))
            db.session.commit()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteImage(id=ql_id)
