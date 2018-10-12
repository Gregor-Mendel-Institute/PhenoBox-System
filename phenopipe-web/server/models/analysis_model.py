import shutil

from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from server.extensions import db
from server.models import ImageModel, BaseModel
from server.utils.util import get_local_path_from_smb


class AnalysisModel(BaseModel):
    __tablename__ = 'analysis'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:The IAP ID of the Analyis results in IAP
    iap_id = db.Column(db.String, unique=True)
    #:The path, as SMB URL, where the exported IAP results are stored
    export_path = db.Column(db.String, nullable=True)
    #:The id of the IAP pipeline with which this analysis has been processed
    pipeline_id = db.Column(db.String, nullable=False)
    #:Timestamp to indicate the start time of the analysis
    started_at = db.Column(db.DateTime, nullable=True)
    #:Timestamp to indicate the end time of the analysis
    finished_at = db.Column(db.DateTime, nullable=True)
    #:Foreign key to the corresponding Timestamp
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding Timestamp
    timestamp = db.relationship("TimestampModel", back_populates="analyses", single_parent=True)
    #:SQLAlchemy relationship to all Postprocessings which have been applied to this analysis
    postprocessings = db.relationship("PostprocessModel", back_populates="analysis", cascade="all, delete-orphan")
    #:SQLAlchemy relationship to all Snapshots processed by this analysis
    db.UniqueConstraint(timestamp_id, pipeline_id, name=u'uq_analysis_timestamp_id_pipeline_id')

    @staticmethod
    def get_or_create(timestamp_id, pipeline_id, session=None):
        if session is None:
            session = db.session
        try:
            return session.query(AnalysisModel).filter_by(timestamp_id=timestamp_id,
                                                          pipeline_id=pipeline_id).one(), False
        except NoResultFound:
            entry = AnalysisModel(timestamp_id, pipeline_id)
            try:
                session.add(entry)
                session.flush()
                return entry, True
            except IntegrityError:
                session.rollback()
                return session.query(AnalysisModel).filter_by(timestamp_id=timestamp_id,
                                                              pipeline_id=pipeline_id).one(), False

    def purge(self):
        shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
        for postprocess in self.postprocessings:
            postprocess.purge()
        local_path = get_local_path_from_smb(self.report_path, shared_folder_map)
        shutil.rmtree(local_path)
        for image in self.timestamp.snapshots.images.where(ImageModel.type == 'segmented'):
            db.session.delete(image)

    def __init__(self, timestamp_id, pipeline_id):
        self.timestamp_id = timestamp_id
        self.pipeline_id = pipeline_id

    def __repr__(self):
        return '<Analysis %d with Pipeline %r of timestamp %d>' % (self.id, self.pipeline_id, self.timestamp_id)
