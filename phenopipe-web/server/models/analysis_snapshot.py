from server.extensions import db
from server.models import BaseModel

association_table = db.Table('analysis_snapshot', BaseModel.metadata,
                             db.Column('analysis_id', db.Integer, db.ForeignKey('analysis.id'), nullable=False,
                                       primary_key=True),
                             db.Column('snapshot_id', db.Integer, db.ForeignKey('snapshot.id'), nullable=False,
                                       primary_key=True)
                             )
