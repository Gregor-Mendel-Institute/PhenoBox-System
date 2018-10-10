import dateutil.parser
import graphene
from flask import logging
from flask_jwt_extended import get_jwt_identity
from graphene import Node
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id
from graphql_relay import to_global_id
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from server.api.exceptions import ForbiddenActionError
from server.api.graphql.exceptions import ConstraintViolationError, UnknownDataError, InvalidMutationRequestError, \
    UnableToDeleteError
from server.api.graphql.sample_group_schema import SampleGroupInput
from server.auth.authentication import is_admin
from server.extensions import db
from server.models import PlantModel
from server.models import SampleGroupModel
from server.models.experiment_model import ExperimentModel


class Experiment(SQLAlchemyObjectType):
    class Meta:
        model = ExperimentModel
        interfaces = (Node,)


class ExperimentInput(graphene.InputObjectType):
    name = graphene.NonNull(graphene.String)
    description = graphene.String()
    scientist = graphene.NonNull(graphene.String)
    group_name = graphene.NonNull(graphene.String)
    start_date = graphene.String()
    start_of_experimentation = graphene.String()
    sample_group_data = graphene.List(SampleGroupInput)


class EditPlantInput(graphene.InputObjectType):
    id = graphene.NonNull(graphene.ID)
    index = graphene.Int()
    name = graphene.String()
    delete = graphene.Boolean()


class EditSampleGroupInput(graphene.InputObjectType):
    id = graphene.NonNull(graphene.ID)
    name = graphene.String()
    description = graphene.String()
    is_control = graphene.Boolean()
    treatment = graphene.NonNull(graphene.String)
    species = graphene.String()
    genotype = graphene.String()
    variety = graphene.String()
    growth_conditions = graphene.String()
    plants = graphene.List(EditPlantInput)
    delete = graphene.Boolean()


class EditProjectInput(graphene.InputObjectType):
    id = graphene.NonNull(graphene.ID)
    name = graphene.String()
    description = graphene.String()
    scientist = graphene.String()
    group_name = graphene.String()
    start_date = graphene.String()
    start_of_experimentation = graphene.String()
    sample_group_data = graphene.List(EditSampleGroupInput)


class CreateExperiment(graphene.Mutation):
    class Input:
        name = graphene.String()
        description = graphene.String()
        scientist = graphene.String()
        group_name = graphene.String()

    id = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    scientist = graphene.String()
    group_name = graphene.String()
    start_date = graphene.String()
    start_of_experimentation = graphene.String()

    def mutate(self, args, context, info):
        name = args.get('name')
        description = args.get('description')
        scientist = args.get('scientist')
        group_name = args.get('group_name')
        experiment = ExperimentModel(name, description, scientist, group_name)
        try:
            db.session.add(experiment)
            db.session.flush()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        db.session.commit()
        return CreateExperiment(id=experiment.id, name=experiment.name, description=experiment.description,
                                scientist=experiment.scientist, group_name=group_name)


class EditProject(graphene.Mutation):
    class Input:
        project_data = graphene.Argument(EditProjectInput)

    experiment = graphene.Field(Experiment)

    @staticmethod
    def _add_new_group(group_data, exp_id):
        group = SampleGroupModel.fromdict(group_data, exp_id)
        db.session.add(group)
        db.session.flush()
        for plant_data in group_data.get('plants'):
            plant = PlantModel(plant_data.get('index'), plant_data.get('name'), group.id)
            db.session.add(plant)
        db.session.flush()  # TODO check if necessary

    @staticmethod
    def _edit_group(group_id, group_data, experiment):
        if 'plants' in group_data:
            plant_list = group_data.pop('plants')

            for plant_data in plant_list:
                ql_plant_id = plant_data.pop('id')
                delete = plant_data.pop('delete', False)
                if delete:
                    if len(experiment.timestamps) == 0:
                        _, plant_id = from_global_id(ql_plant_id)
                        try:
                            plant = db.session.query(PlantModel).join(SampleGroupModel) \
                                .filter(PlantModel.id == plant_id) \
                                .filter(SampleGroupModel.experiment_id == experiment.id) \
                                .one()
                            db.session.delete(plant)
                        except NoResultFound as e:
                            raise InvalidMutationRequestError("The given plant to delete was not found")
                    else:
                        raise UnableToDeleteError(
                            "Unable to delete plant because there already exists at least one timestamp")
                elif ql_plant_id == '' and len(experiment.timestamps) == 0:
                    plant = PlantModel(plant_data.get('index'), plant_data.get('name'),
                                       group_id)
                    db.session.add(plant)
                else:
                    _, plant_id = from_global_id(ql_plant_id)
                    try:
                        plant_row = db.session.query(PlantModel) \
                            .join(SampleGroupModel) \
                            .filter(PlantModel.id == plant_id) \
                            .filter(SampleGroupModel.experiment_id == experiment.id) \
                            .one()
                        for key in plant_data:
                            setattr(plant_row, key, plant_data[key])
                    except NoResultFound as e:
                        raise InvalidMutationRequestError("The given plant to edit was not found")
                db.session.flush()  # TODO Check if necessary
        group_row = SampleGroupModel.query.filter_by(id=group_id).one()
        for key in group_data:
            setattr(group_row, key, group_data[key])
        db.session.flush()  # TODO Check if necessary

    @staticmethod
    def _edit_experiment(proj_data, experiment):
        if 'sample_group_data' in proj_data:
            group_list = proj_data.pop('sample_group_data')
            for group_data in group_list:
                ql_group_id = group_data.pop('id')
                if ql_group_id == '' and len(experiment.timestamps) == 0:  # New group
                    EditProject._add_new_group(group_data, experiment.id)
                else:  # Existing group
                    _, group_id = from_global_id(ql_group_id)
                    delete = group_data.pop('delete', False)
                    if delete:
                        if len(experiment.timestamps) == 0:
                            try:
                                group = db.session.query(SampleGroupModel) \
                                    .filter(SampleGroupModel.id == group_id) \
                                    .filter(SampleGroupModel.experiment_id == experiment.id) \
                                    .one()
                                db.session.delete(group)
                            except NoResultFound as e:
                                raise InvalidMutationRequestError("The given sampple group to delete was not found")
                        else:
                            raise UnableToDeleteError(
                                "Unable to delete sample group because there already exists at least one timestamp")
                    else:
                        EditProject._edit_group(group_id, group_data, experiment)
        for key in proj_data:
            # TODO validate datestrings
            # TODO disallow name changes after an analysis is present to prevent IAP entries getting out of sync?
            if key == 'start_of_experimentation':
                try:
                    parsed = dateutil.parser.parse(proj_data[key])
                except ValueError as e:
                    setattr(experiment, key, None)
                    continue
            setattr(experiment, key, proj_data[key])
        db.session.flush()

    def mutate(self, args, context, info):
        identity = get_jwt_identity()
        proj_data = args.get('project_data')
        _, exp_id = from_global_id(proj_data.pop('id'))
        with db.session.no_autoflush:
            try:
                experiment = db.session.query(ExperimentModel).get(exp_id)
                if experiment.scientist == identity.get('username') or is_admin(identity):
                    EditProject._edit_experiment(proj_data, experiment)
                else:
                    raise ForbiddenActionError(
                        "Unable to edit experiment {} by user {}. Insufficient priviliges.".format(
                            experiment.name, identity.get('username'))
                        , identity.get('username'))
                    # User is not allowed to edit this project
                db.session.commit()
                return EditProject(experiment=experiment)
            except IntegrityError as err:
                db.session.rollback()
                #TODO add experiment name constraint
                if err.orig.diag.constraint_name == u'uq_sample_groups_treatment_experiment_id':
                    raise ConstraintViolationError('It is not allowed to have two sample groups with the same '
                                                   'treatment.')
                elif err.orig.diag.constraint_name == u'sample_group_name_experiment_id_key':
                    raise ConstraintViolationError('It is not allowed to have two sample groups with the same '
                                                   'name.')
            except DBAPIError as err:
                logging.getLogger(__name__).exception("An unexpected DB error occured")
                db.session.rollback()
                raise UnknownDataError("An unexpected DB error occured")


class ConstructExperiment(graphene.Mutation):
    class Input:
        experiment_data = graphene.Argument(ExperimentInput)

    id = graphene.ID()

    def mutate(self, args, context, info):
        exp_data = args.get('experiment_data')
        sample_group_data = exp_data.get('sample_group_data')

        try:
            experiment = ExperimentModel(exp_data.get('name'), exp_data.get('description'), exp_data.get('scientist'),
                                         exp_data.get('group_name'), exp_data.get('start_date'), exp_data.get('start_of_experimentation'))
            db.session.add(experiment)
            db.session.flush()
            for group_data in sample_group_data:
                group = SampleGroupModel.fromdict(group_data, experiment.id)
                db.session.add(group)
                db.session.flush()
                for plant_data in group_data.get('plants'):
                    plant = PlantModel(plant_data.get('index'), plant_data.get('name'), group.id)
                    db.session.add(plant)
        except DBAPIError as err:
            #TODO add unique constraint checks
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        db.session.commit()
        return ConstructExperiment(id=to_global_id('Experiment', experiment.id))


class DeleteExperiment(graphene.Mutation):
    class Input:
        id = graphene.ID()

    id = graphene.ID()

    def mutate(self, args, context, info):
        ql_id = args.get('id')
        _, id = from_global_id(ql_id)
        try:
            experiment = db.session.query(ExperimentModel).get(id)
            if len(experiment.timestamps) > 0:
                raise UnableToDeleteError(
                    "Experiment could not be deleted because there are timestamps associated with it")
            db.session.delete(experiment)
            db.session.commit()
        except DBAPIError as err:
            logging.getLogger(__name__).exception("An unexpected DB error occured")
            db.session.rollback()
            raise UnknownDataError("An unexpected DB error occured")

        return DeleteExperiment(id=ql_id)
