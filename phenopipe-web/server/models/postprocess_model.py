import shutil

from flask import current_app
from psycopg2._psycopg import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from server.extensions import db
from server.models import BaseModel
from server.utils.util import get_local_path_from_smb


class PostprocessModel(BaseModel):
    __tablename__ = 'postprocess'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    snapshot_hash = db.Column(db.BIGINT, nullable=False)
    #:Path, as SMB URL, to the results of this postprocess
    result_path = db.Column(db.String, nullable=True)
    #:The ID of the postprocess that was applied
    postprocessing_stack_id = db.Column(db.String, nullable=False)
    #:The ID of the sample group used as control group
    control_group_id = db.Column(db.Integer, db.ForeignKey("sample_group.id"), nullable=False)
    #:Timestamp to indicate the start time of the postprocessing
    started_at = db.Column(db.DateTime, nullable=True)
    #:Timestamp to indicate the end time of the postprocessing
    finished_at = db.Column(db.DateTime, nullable=True)
    #:A note from the user to make it easier to identify a postprocess
    note = db.Column(db.Text, nullable=True)
    #:Foreign key to the corresponding analysis
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding analysis
    analysis = db.relationship("AnalysisModel", back_populates="postprocessings", single_parent=True)
    #:SQLAlchemy relationship to all Snapshots processed by this postprocess
    snapshots = db.relationship("SnapshotModel", secondary='postprocess_snapshot', back_populates='postprocesses')
    #:SQLAlchemy relationship to the sample group used as control group
    control_group = db.relationship("SampleGroupModel")

    db.UniqueConstraint(snapshot_hash, postprocessing_stack_id, analysis_id, control_group_id)

    def purge(self):
        shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
        local_path = get_local_path_from_smb(self.result_path, shared_folder_map)
        shutil.rmtree(local_path)

    @staticmethod
    def calculate_snapshot_hash(snapshots):
        return hash(frozenset([snapshot.id for snapshot in snapshots]))

    @staticmethod
    def get_or_create(analysis_id, postprocessing_stack_id, control_group_id, snapshots, session=None):
        snap_hash = PostprocessModel.calculate_snapshot_hash(snapshots)
        if session is None:
            session = db.session
        try:
            return session.query(PostprocessModel).filter_by(analysis_id=analysis_id,
                                                             postprocessing_stack_id=postprocessing_stack_id,
                                                             snapshot_hash=snap_hash).one(), False
        except NoResultFound:
            entry = PostprocessModel(analysis_id, postprocessing_stack_id, control_group_id, snapshots, snap_hash)
            try:
                session.add(entry)
                session.flush()
                return entry, True
            except IntegrityError:
                session.rollback()
                return session.query(PostprocessModel).filter_by(analyis_id=analysis_id,
                                                                 postprocessing_stack_id=postprocessing_stack_id,
                                                                 snapshot_hash=snap_hash).one(), False

    def __init__(self, analysis_id, postprocessing_stack_id, control_group_id, snapshots, snapshot_hash=None):
        self.analysis_id = analysis_id
        self.postprocessing_stack_id = postprocessing_stack_id
        self.control_group_id = control_group_id
        self.snapshots = snapshots
        if snapshot_hash is not None:
            self.snapshot_hash = snapshot_hash
        else:
            self.snapshot_hash = self.calculate_snapshot_hash(snapshots)

    def __repr__(self):
        return '<Postprocessing %d with stack %r of analysis %d>' % (
            self.id, self.postprocessing_stack_id, self.analysis_id)
