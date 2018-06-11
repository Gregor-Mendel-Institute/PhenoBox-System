import os

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM, UUID

from server.extensions import db
from server.models import BaseModel
from server.utils.util import get_local_path_from_smb


class SnapshotModel(BaseModel):
    __tablename__ = 'snapshot'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:Metadata for IAP
    measurement_tool = db.Column(db.String)
    #:The ID of the phenobox which was used to create this snapshot
    phenobox_id = db.Column(UUID(as_uuid=True), nullable=False)
    #:Metadata for IAP
    camera_position = db.Column(
        ENUM('vis.side', 'vis.top', 'fluo.top', 'fluo.side', 'nir.top', 'nir.side', 'ir.top', 'ir.side',
             name='camera_position_enum'), nullable=False,
        server_default='vis.side')
    #:Flag used to exclude this snapshot from analysis
    excluded = db.Column(db.Boolean, server_default='f', default=False, nullable=False)
    #:Foreign key to the corresponding Timestamp
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding Timestamp
    timestamp = db.relationship("TimestampModel", back_populates="snapshots", single_parent=True)
    #:Foreign key to the corresponding Timestamp
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding Plant
    plant = db.relationship("PlantModel", back_populates="snapshots", single_parent=True)
    #:SQLAlchemy relationship to all images belonging to this snapshot
    images = db.relationship("ImageModel", back_populates="snapshot", cascade="all, delete-orphan", lazy='dynamic')
    #:SQLAlchemy relationship to all analyses performed on this snapshot
    postprocesses = db.relationship("PostprocessModel", secondary='postprocess_snapshot', back_populates='snapshots')

    db.UniqueConstraint(plant_id, timestamp_id, name=u'uq_snapshot_plant_id_timestamp_id')

    def purge(self):
        # Only allow to delete a snapshot from an uncompleted timestamp
        if not self.timestamp.completed:
            shared_folder_map = current_app.config['SHARED_FOLDER_MAP']
            raw_image_path = None
            for image in self.images:
                if image.type == 'raw':
                    if raw_image_path is None:
                        raw_image_path = get_local_path_from_smb(image.path, shared_folder_map)
                    os.remove(os.path.join(raw_image_path, image.filename))
                db.session.delete(image)
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            return False  # TODO throw exceptions instead of returning true or false

    def __init__(self, plant_id, timestamp_id, camera_position, measurement_tool, phenobox_id):
        self.plant_id = plant_id
        self.timestamp_id = timestamp_id
        self.camera_position = camera_position
        self.measurement_tool = measurement_tool
        self.phenobox_id = phenobox_id

    def __repr__(self):
        return '<Snapshot %d of plant %r>' % (self.id, self.plant.name)
