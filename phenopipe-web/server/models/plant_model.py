from sqlalchemy.ext.hybrid import hybrid_property

from server.extensions import db
from server.models import BaseModel


class PlantModel(BaseModel):
    __tablename__ = 'plant'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:The detailed name of the plant
    name = db.Column(db.String(80))
    #:The index of the plant in the group
    index = db.Column(db.Integer)
    #:Foreign key to the corresponding Sample Group
    sample_group_id = db.Column(db.Integer, db.ForeignKey('sample_group.id'))
    #:SQLAlchemy relationship to the corresponding Sample Group
    sample_group = db.relationship("SampleGroupModel", back_populates="plants", single_parent=True)
    #:SQLAlchemy relationship to all Snapshots that belong to this plant
    snapshots = db.relationship("SnapshotModel", back_populates="plant", cascade="all, delete-orphan")

    db.UniqueConstraint(index, sample_group_id)

    @hybrid_property
    def full_name(self):
        if self.name != '':
            return '{}_{}_{}'.format(self.sample_group.name, self.index, self.name)
        else:
            return '{}_{}'.format(self.sample_group.name, self.index)

    def purge(self):
        for snapshot in self.snapshots:
            snapshot.purge()

    def __init__(self, index, name, sample_group_id):
        self.index = index
        self.name = name
        self.sample_group_id = sample_group_id

    def __repr__(self):
        return '<Plant %r>' % self.name
