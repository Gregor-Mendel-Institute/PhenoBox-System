import graphene
from flask import logging
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id
from sqlalchemy.exc import IntegrityError, DBAPIError

from server.api.graphql.exceptions import UnknownDataError
from server.extensions import db
from server.models.plant_model import PlantModel


class Plant(SQLAlchemyObjectType):
    class Meta:
        model = PlantModel
        interfaces = (Node,)

    full_name = graphene.String()

    def resolve_full_name(self, args, context, info):
        return self.full_name


class PlantInput(graphene.InputObjectType):
    index = graphene.NonNull(graphene.Int)
    name = graphene.NonNull(graphene.String)


class CreatePlant(graphene.Mutation):
    class Input:
        index = graphene.Int()
        name = graphene.String()
        sample_group_id = graphene.Int()

    id = graphene.Int()
    index = graphene.Int()
    name = graphene.String()
    sample_group_id = graphene.Int()

    def mutate(self, args, context, info):
        index = args.get('index')
        name = args.get('name')
        sample_group_id = args.get('sample_group_id')
        plant = PlantModel(index, name, sample_group_id)

        try:
            db.session.add(plant)
            db.session.flush()
        except IntegrityError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        except DBAPIError:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        db.session.commit()

        return CreatePlant(id=plant.id, index=plant.index, name=plant.name, sample_group_id=plant.sample_group_id)


class DeletePlant(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(PlantModel).get(id))
            db.session.commit()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeletePlant(id=ql_id)
