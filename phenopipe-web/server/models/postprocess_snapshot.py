from server.extensions import db
from server.models import BaseModel

postprocess_snapshot_assoc = db.Table('postprocess_snapshot', BaseModel.metadata,
                             db.Column('postprocess_id', db.Integer, db.ForeignKey('postprocess.id'), nullable=False,
                                       primary_key=True),
                             db.Column('snapshot_id', db.Integer, db.ForeignKey('snapshot.id'), nullable=False,
                                       primary_key=True)
                             )
