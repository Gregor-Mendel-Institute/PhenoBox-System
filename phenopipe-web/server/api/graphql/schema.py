import graphene
from flask import current_app
from flask_jwt_extended import get_jwt_identity
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import GraphQLError
from graphql_relay import from_global_id
from rq.job import Job as RQJob
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager

from server.api.graphql.analysis_schema import Analysis
from server.api.graphql.experiment_schema import Experiment, CreateExperiment, DeleteExperiment, ConstructExperiment, \
    EditProject
from server.api.graphql.image_schema import Image, AddImage
from server.api.graphql.pipeline_schema import Pipeline, PipelineConnection
from server.api.graphql.plant_schema import Plant, CreatePlant, DeletePlant
from server.api.graphql.postprocess_schema import Postprocess
from server.api.graphql.postprocessing_stack_schema import PostprocessingStack, PostprocessingStackConnection, \
    PostprocessingScript
from server.api.graphql.rq_job_schema import Job
from server.api.graphql.sample_group_schema import SampleGroup, CreateSampleGroup, DeleteSampleGroup
from server.api.graphql.snapshot_schema import CreateSnapshot, Snapshot, DeleteSnapshot, ChangeSnapshotExclusion
from server.api.graphql.task_schema import Task, TaskConnection
from server.api.graphql.timestamp_schema import Timestamp, CompleteTimestamp
from server.auth.authentication import is_admin
from server.extensions import db, redis_db, get_analysis_task_scheduler, get_postprocess_task_scheduler, \
    analysis_job_queue, postprocessing_job_queue
from server.models import ExperimentModel, TimestampModel, SnapshotModel, SampleGroupModel, PlantModel, ImageModel, \
    AnalysisModel, PostprocessModel
from server.modules.processing.analysis.analysis import get_iap_pipelines
from server.modules.processing.analysis.analysis_task import AnalysisTask
from server.modules.processing.postprocessing.postprocessing import get_postprocessing_stacks
from server.modules.processing.postprocessing.postprocessing_task import PostprocessingTask
from server.modules.processing.remote_exceptions import UnavailableError


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    experiment = relay.Node.Field(Experiment)
    plant = relay.Node.Field(Plant)
    sample_group = relay.Node.Field(SampleGroup)
    snapshot = relay.Node.Field(Snapshot)
    timestamp = relay.Node.Field(Timestamp)
    image = relay.Node.Field(Image)
    analysis = relay.Node.Field(Analysis)
    postprocess = relay.Node.Field(Postprocess)
    postprocessing_task = graphene.Field(Task, id=graphene.NonNull(graphene.ID))
    analysis_task = graphene.Field(Task, id=graphene.NonNull(graphene.ID))

    job = graphene.Field(Job, id=graphene.NonNull(graphene.ID))
    analysis_job = graphene.Field(Job, id=graphene.NonNull(graphene.ID))
    postprocessing_job = graphene.Field(Job, id=graphene.NonNull(graphene.ID))

    experiments = SQLAlchemyConnectionField(Experiment, with_name=graphene.String(), with_scientist=graphene.String())
    plants = SQLAlchemyConnectionField(Plant)
    sample_groups = SQLAlchemyConnectionField(SampleGroup, for_timestamp=graphene.ID(), for_analysis=graphene.ID(),
                                              for_postprocess=graphene.ID())
    snapshots = SQLAlchemyConnectionField(Snapshot, for_timestamp=graphene.ID(), with_camera_position=graphene.String(),
                                          with_measurement_tool=graphene.String(),
                                          for_open_timestamp=graphene.Boolean(),
                                          for_plant=graphene.ID())
    timestamps = SQLAlchemyConnectionField(Timestamp, for_experiment=graphene.ID(), ordered=graphene.Boolean())
    images = SQLAlchemyConnectionField(Image, for_snapshot=graphene.ID())
    analyses = SQLAlchemyConnectionField(Analysis, for_timestamp=graphene.ID())
    postprocessings = SQLAlchemyConnectionField(Postprocess, for_analysis=graphene.ID())

    postprocessing_stacks = graphene.ConnectionField(PostprocessingStackConnection, unused_for_analysis=graphene.ID())
    pipelines = graphene.ConnectionField(PipelineConnection, unused_for_timestamp=graphene.ID())

    analysis_tasks = graphene.ConnectionField(TaskConnection)
    postprocessing_tasks = graphene.ConnectionField(TaskConnection)

    # TODO Use Exceptions all over the schema and adapt clients to use them

    def resolve_analysis_task(self, args, context, info):
        _, key = from_global_id(args.get('id'))
        task = AnalysisTask.from_key(redis_db, key)
        return Task.from_task_object(task)

    def resolve_postprocessing_task(self, args, context, info):
        _, key = from_global_id(args.get('id'))
        task = PostprocessingTask.from_key(redis_db, key)
        return Task.from_task_object(task)

    def resolve_job(self, args, context, info):
        _, job_id = from_global_id(args.get('id'))
        return Job.from_rq_job_instance(RQJob.fetch(job_id, redis_db))

    def resolve_analysis_job(self, args, context, info):
        _, job_id = from_global_id(args.get('id'))
        return Job.from_rq_job_instance(analysis_job_queue.fetch_job(job_id))

    def resolve_postprocessing_job(self, args, context, info):
        _, job_id = from_global_id(args.get('id'))
        return Job.from_rq_job_instance(postprocessing_job_queue.fetch_job(job_id))

    def resolve_experiments(self, args, context, info):
        conds = list()
        query = db.session.query(ExperimentModel)
        identity = get_jwt_identity()
        if not is_admin(identity) and 'with_scientist' in args:
            raise GraphQLError('Filtering by scientist is only allowed as admin')

        if 'with_scientist' in args:
            scientist = args.get('with_scientist')
            conds[0] = ExperimentModel.scientist.like('{}'.format(scientist))
        else:
            conds.append(ExperimentModel.scientist.like('{}'.format(identity.get('username'))))
        if 'with_name' in args:
            name = args.get('with_name')
            conds.append(ExperimentModel.name.like('{}'.format(name)))

        for cond in conds:
            query = query.filter(cond)
        return query.all()

    def resolve_timestamps(self, args, context, info):
        cond = True
        if 'for_experiment' in args:
            experiment_id = args.get('for_experiment')
            _, experiment_db_id = from_global_id(experiment_id)
            cond = (TimestampModel.experiment_id == experiment_db_id)
        if 'ordered' in args and args.get('ordered') == True:
            return db.session.query(TimestampModel).filter(cond).order_by(TimestampModel.created_at).all()

        return db.session.query(TimestampModel).filter(cond).all()

    def resolve_snapshots(self, args, context, info):
        conds = list()
        query = db.session.query(SnapshotModel)
        if 'for_open_timestamp' in args:
            query = query.join(TimestampModel)
            conds.append(TimestampModel.completed.is_(False))
        if 'for_timestamp' in args:
            timestamp_id = args.get('for_timestamp')
            _, timestamp_db_id = from_global_id(timestamp_id)
            conds.append((SnapshotModel.timestamp_id == timestamp_db_id))
        if 'for_plant' in args:
            _, plant_db_id = from_global_id(args.get('for_plant'))
            conds.append((SnapshotModel.plant_id == plant_db_id))
        if 'with_camera_position' in args:
            conds.append((SnapshotModel.camera_position == args.get('with_camera_position')))
        if 'with_measurement_tool' in args:
            conds.append((SnapshotModel.measurement_tool == args.get('with_measurement_tool')))

        for cond in conds:
            query = query.filter(cond)
        return query.all()

    def resolve_images(self, args, context, info):
        cond = True
        if 'for_snapshot' in args:
            snapshot_id = args.get('for_snapshot')
            _, snapshot_db_id = from_global_id(snapshot_id)
            cond = (ImageModel.snapshot_id == snapshot_db_id)
        # TODO add filter for type

        return db.session.query(ImageModel).filter(cond).all()

    def resolve_analyses(self, args, context, info):
        cond = True
        if 'for_timestamp' in args:
            timestamp_id = args.get('for_timestamp')
            _, timestamp_db_id = from_global_id(timestamp_id)
            cond = (AnalysisModel.timestamp_id == timestamp_db_id)

        return db.session.query(AnalysisModel).filter(cond).all()

    def resolve_postprocessings(self, args, context, info):
        cond = True
        if 'for_analysis' in args:
            analysis_id = args.get('for_analysis')
            _, analysis_db_id = from_global_id(analysis_id)
            cond = (PostprocessModel.analysis_id == analysis_db_id)

        return db.session.query(PostprocessModel).filter(cond).all()

    def resolve_sample_groups(self, args, context, info):
        cond = True
        if 'for_timestamp' in args:
            timestamp_id = args.get('for_timestamp')
            _, timestamp_db_id = from_global_id(timestamp_id)

            groups = db.session.query(SampleGroupModel) \
                .join(PlantModel) \
                .join(SnapshotModel,
                      and_(
                          SnapshotModel.plant_id == PlantModel.id,
                          SnapshotModel.timestamp_id == timestamp_db_id)
                      ) \
                .options(
                contains_eager("plants"),
                contains_eager("plants.snapshots"),
            )
            return groups.all()
        elif 'for_analysis' in args:
            analysis_id = args.get('for_analysis')
            _, analysis_db_id = from_global_id(analysis_id)

            groups = db.session.query(SampleGroupModel) \
                .join(PlantModel) \
                .join(SnapshotModel,
                      and_(
                          SnapshotModel.plant_id == PlantModel.id,
                          SnapshotModel.analyses.any(AnalysisModel.id == analysis_db_id)
                      )) \
                .join(AnalysisModel, SnapshotModel.analyses.any(AnalysisModel.id == analysis_db_id)) \
                .options(
                contains_eager("plants"),
                contains_eager("plants.snapshots"),
            )
            return groups.all()
        elif 'for_postprocess' in args:
            postprocess_id = args.get('for_postprocess')
            _, postprocess_db_id = from_global_id(postprocess_id)

            groups = db.session.query(SampleGroupModel) \
                .join(PlantModel) \
                .join(SnapshotModel,
                      and_(
                          SnapshotModel.plant_id == PlantModel.id,
                          SnapshotModel.postprocesses.any(PostprocessModel.id == postprocess_db_id)
                      )) \
                .join(PostprocessModel, SnapshotModel.analyses.any(PostprocessModel.id == postprocess_db_id)) \
                .options(
                contains_eager("plants"),
                contains_eager("plants.snapshots"),
            )
            return groups.all()
        return db.session.query(SampleGroupModel).filter(cond).all()

    def resolve_postprocessing_stacks(self, args, context, info):
        try:
            identity = get_jwt_identity()
            grpc_stacks = get_postprocessing_stacks(identity.get('username'))
            analysis_db_id = None
            snapshot_hash = None
            if 'unused_for_analysis' in args:
                analysis_id = args.get('unused_for_analysis')
                _, analysis_db_id = from_global_id(analysis_id)
                snapshots = db.session.query(SnapshotModel).join(TimestampModel) \
                    .filter(SnapshotModel.excluded == False) \
                    .filter(TimestampModel.analyses.any(AnalysisModel.id == analysis_db_id)) \
                    .all()
                snapshot_hash = PostprocessModel.calculate_snapshot_hash(snapshots)

            stacks = list()
            for stack in grpc_stacks:
                postprocess = None
                if analysis_db_id is not None:  # Filter
                    postprocess = db.session.query(PostprocessModel) \
                        .filter(PostprocessModel.analysis_id == analysis_db_id) \
                        .filter(PostprocessModel.postprocessing_stack_id == stack.id) \
                        .filter(PostprocessModel.snapshot_hash == snapshot_hash) \
                        .first()
                if postprocess is None:
                    stacks.append(PostprocessingStack.from_grpc_type(stack))
            return stacks
        except UnavailableError as e:
            raise

    def resolve_pipelines(self, args, context, info):
        try:
            identity = get_jwt_identity()
            grpc_pipelines = get_iap_pipelines(identity.get('username'))
            timestamp_db_id = None
            if 'unused_for_timestamp' in args:
                timestamp_id = args.get('unused_for_timestamp')
                _, timestamp_db_id = from_global_id(timestamp_id)
            pipelines = list()
            for pipeline in grpc_pipelines:
                analysis = None
                if timestamp_db_id is not None:  # Filter
                    analysis = db.session.query(AnalysisModel).filter(
                        AnalysisModel.timestamp_id == timestamp_db_id).filter(
                        AnalysisModel.pipeline_id == pipeline.id).first()
                if analysis is None:
                    pipelines.append(Pipeline.from_grpc_type(pipeline))
            return pipelines
        except UnavailableError as e:
            raise

    def resolve_analysis_tasks(self, args, context, info):
        identity = get_jwt_identity()
        username = identity.get('username')
        if username is None and not current_app.config['PRODUCTION']:
            username = 'a'
        tasks = get_analysis_task_scheduler().fetch_all_tasks(username)
        return [Task.from_task_object(task) for task in tasks]

    def resolve_postprocessing_tasks(self, args, context, info):
        identity = get_jwt_identity()
        username = identity.get('username')
        if username is None and not current_app.config['PRODUCTION']:
            username = 'a'
        tasks = get_postprocess_task_scheduler().fetch_all_tasks(username)
        return [Task.from_task_object(task) for task in tasks]


class Mutation(graphene.ObjectType):
    construct_experiment = ConstructExperiment.Field()
    create_experiment = CreateExperiment.Field()
    create_sample_group = CreateSampleGroup.Field()
    create_plant = CreatePlant.Field()
    create_snapshot = CreateSnapshot.Field()
    complete_timestamp = CompleteTimestamp.Field()
    add_image = AddImage.Field()

    edit_project = EditProject.Field()
    change_snapshot_exclusion = ChangeSnapshotExclusion.Field()

    delete_experiment = DeleteExperiment.Field()
    delete_plant = DeletePlant.Field()
    delete_sample_group = DeleteSampleGroup.Field()
    # delete_timestamp = DeleteTimestamp.Field()
    delete_snapshot = DeleteSnapshot.Field()
    # delete_image = DeleteImage.Field()


schema = graphene.Schema(query=Query, mutation=Mutation,
                         types=[Experiment, Plant, SampleGroup, Snapshot, Image, Timestamp, Analysis, Postprocess,
                                PostprocessingStack, PostprocessingScript, Task])
