from server.extensions import db
from server.models import BaseModel


class ExperimentModel(BaseModel):
    __tablename__ = 'experiment'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:The name of the experiment
    name = db.Column(db.String(80))
    #:A detailed description of the experiment
    description = db.Column(db.Text)
    #:The username of the scientist conducting this experiment
    scientist = db.Column(db.String(120))
    #:The name of the research group the scientist belongs to
    group_name = db.Column(db.String(120))
    # e.g. Date of seeding
    #:The day the experiment starts
    start_date = db.Column(db.DateTime, server_default=db.func.timezone('UTC', db.func.current_timestamp()))
    # e.g. Date of vernalisation
    #:An alternate date for the start of the analysis timeline
    start_of_experimentation = db.Column(db.DateTime, nullable=True)
    #:SQLAlchemy relationship to all Sample Groups which belong to this experiment
    sample_groups = db.relationship("SampleGroupModel", back_populates="experiment", cascade="all, delete-orphan", )
    #:SQLAlchemy relationship to all Timestamps which belong to this experiment
    timestamps = db.relationship("TimestampModel", order_by="TimestampModel.created_at",
                                 back_populates="experiment", cascade="all, delete-orphan")

    db.UniqueConstraint(name, scientist, name=u'uq_experiment_name_scientist')

    # def purge(self):
    #     # check for running analysis or postprocessing tasks
    #     # if none --> purge
    #     # Check if there is job which operates on the corresponding timestamp
    #     for timestamp in self.timestamps:
    #         if analysis.is_job_running_for_user(self.scientist, timestamp):
    #             return False  # TODO throw exception
    #         for ana in timestamp.analyses:
    #             if postprocessing.is_job_running_for_user(self.scientist, ana.id):
    #                 return False  # TODO Throw exception
    #     iap_stub = phenopipe_iap_pb2_grpc.PhenopipeIapStub(get_iap_channel())
    #     pipe_stub = phenopipe_pb2_grpc.PhenopipeStub(get_iap_channel())
    #     job_ids = list()
    #     # Delete from IAP
    #     for timestamp in self.timestamps:
    #         response = iap_stub.DeleteExperiment(
    #             phenopipe_iap_pb2.DeleteRequest(experiment_id=timestamp.iap_exp_id)
    #         )
    #         job_ids.append(response.job_id)
    #
    #     for job_id in job_ids:
    #         request = phenopipe_pb2.WatchJobRequest(
    #             job_id=job_id
    #         )
    #         status = pipe_stub.WatchJob(request)
    #         for msg in status:
    #             print(msg)
    #
    #         response = iap_stub.FetchAnalyzeResult(
    #             phenopipe_pb2.FetchJobResultRequest(job_id=job_id)
    #         )
    #         # TODO catch grpc errors
    #
    #
    #         # Delete other entries
    #         # delete itself

    def __init__(self, name, description, scientist, group_name, start_date, start_of_experimentation):
        self.name = name
        self.description = description
        self.scientist = scientist
        self.group_name = group_name
        self.start_date = start_date
        self.start_of_experimentation = start_of_experimentation

    def __repr__(self):
        return '<Experiment %r>' % self.name
