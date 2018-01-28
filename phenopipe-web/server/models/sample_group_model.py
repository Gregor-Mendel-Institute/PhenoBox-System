from server.extensions import db
from server.models import BaseModel


class SampleGroupModel(BaseModel):
    __tablename__ = 'sample_group'
    #:Primary key of the Model
    id = db.Column(db.Integer, primary_key=True)
    #:The name of the sample group
    name = db.Column(db.String(80), nullable=False)
    #:A detailed description of the group
    description = db.Column(db.Text)
    #:Metadata for IAP
    species = db.Column(db.String)
    #:Metadata for IAP
    genotype = db.Column(db.String)
    #:Metadata for IAP
    variety = db.Column(db.String)
    #:Metadata for IAP
    growth_conditions = db.Column(db.String)
    #:Metadata for IAP
    treatment = db.Column(db.String, nullable=True)  # TODO change to False after all values have been updated
    #:Indicates whether this group is a control group or not
    is_control = db.Column(db.Boolean, nullable=False, default=False, server_default='f')
    #:Foreign key to the corresponding Experiment
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'), nullable=False)
    #:SQLAlchemy relationship to the corresponding Experiment
    experiment = db.relationship("ExperimentModel", back_populates="sample_groups", single_parent=True)
    #:SQLAlchemy relationship to all plants belonging to this sample group
    plants = db.relationship("PlantModel", back_populates="sample_group", cascade="all, delete-orphan")

    db.UniqueConstraint(name, experiment_id)
    db.UniqueConstraint(treatment, experiment_id)

    def __init__(self, name, treatment, description, species, genotype, variety, growth_conditions, experiment_id,
                 is_control=False):
        if name and name.strip() == "":
            name = None
        if treatment and treatment.strip() == "":
            treatment = None

        self.name = name
        self.treatment = treatment
        self.description = description
        self.experiment_id = experiment_id
        self.species = species
        self.genotype = genotype
        self.variety = variety
        self.growth_conditions = growth_conditions
        self.is_control = is_control

    @classmethod
    def fromdict(self, group_data, experiment_id):
        for key, value in group_data.items():
            if type(value) is unicode and value.strip() == "":
                del group_data[key]
        return self(
            group_data.get('name'), group_data.get('treatment'), group_data.get('description'),
            group_data.get('species'),
            group_data.get('genotype'), group_data.get('variety'), group_data.get('growth_conditions'),
            experiment_id=experiment_id, is_control=group_data.get('is_control'))

    def __repr__(self):
        return '<SampleGroup %r>' % self.name
