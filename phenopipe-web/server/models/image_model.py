from sqlalchemy.dialects.postgresql import ENUM

from server.extensions import db
from server.models import BaseModel


class ImageModel(BaseModel):
    __tablename__ = 'image'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:The path, as SMB URL, to the image file
    path = db.Column(db.String, nullable=False)
    #:The filename of the image
    filename = db.Column(db.String, nullable=False)
    #:The type of the image. Indicates whether this image was processed or not
    type = db.Column(ENUM('raw', 'segmented', name='image_type_enum'), default="raw", server_default='raw',
                     nullable=False)
    #:The angle at which the image was taken
    angle = db.Column(db.Integer, nullable=False)
    #:Foreign key to the corresponding Snapshot
    snapshot_id = db.Column(db.Integer, db.ForeignKey('snapshot.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding Snapshot
    snapshot = db.relationship("SnapshotModel", back_populates="images", single_parent=True)

    # TODO add unique constraint for snapshot_id and path+filename
    def __init__(self, snapshot_id, path, filename, angle, image_type):
        self.snapshot_id = snapshot_id
        self.path = path
        self.filename = filename
        self.type = image_type
        self.angle = angle

    def __repr__(self):
        return '<Image %d of plant %r>' % (self.id, self.filename)
