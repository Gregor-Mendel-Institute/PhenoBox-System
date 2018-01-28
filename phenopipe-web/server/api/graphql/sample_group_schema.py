import graphene
from flask import logging
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id
from sqlalchemy.exc import IntegrityError, DBAPIError

from server.api.graphql.exceptions import UnknownDataError
from server.api.graphql.plant_schema import PlantInput
from server.extensions import db
from server.models.sample_group_model import SampleGroupModel


class SampleGroup(SQLAlchemyObjectType):
    class Meta:
        model = SampleGroupModel
        interfaces = (Node,)


class SampleGroupInput(graphene.InputObjectType):
    name = graphene.NonNull(graphene.String)
    description = graphene.String()
    treatment = graphene.NonNull(graphene.String)
    species = graphene.String()
    genotype = graphene.String()
    variety = graphene.String()
    growth_conditions = graphene.String()
    is_control = graphene.Boolean()
    plants = graphene.List(PlantInput)


class CreateSampleGroup(graphene.Mutation):
    class Input:
        group_data = graphene.Argument(SampleGroupInput)
        experiment_id = graphene.NonNull(graphene.ID)

    id = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    treatment = graphene.String()
    species = graphene.String()
    genotype = graphene.String()
    variety = graphene.String()
    growth_conditions = graphene.String()
    is_control = graphene.Boolean()
    experiment_id = graphene.Int()

    def mutate(self, args, context, info):
        sample_group = SampleGroupModel.fromdict(args.get('group_data'), args.get('experiment_id'))
        try:
            db.session.add(sample_group)
            db.session.flush()
        except IntegrityError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")
        db.session.commit()
        return CreateSampleGroup(id=sample_group.id, name=sample_group.name, treatment=sample_group.treatment,
                                 description=sample_group.description,
                                 species=sample_group.speciesm, genotype=sample_group.genotype,
                                 variety=sample_group.variety,
                                 growth_conditions=sample_group.growth_conditions, is_control=sample_group.is_control,
                                 experiment_id=sample_group.experiment_id)


class DeleteSampleGroup(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            db.session.delete(db.session.query(SampleGroupModel).get(id))
            db.session.commit()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteSampleGroup(id=ql_id)
