from sqlalchemy import MetaData

from server.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    meta = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })
    #:Timestamp indicating the time this row was created
    created_at = db.Column(db.DateTime, server_default=db.func.timezone('UTC', db.func.current_timestamp()))
    #:Timestamp indicating the last time this row was changed
    updated_at = db.Column(db.DateTime,
                           server_default=db.func.timezone('UTC', db.func.current_timestamp()),
                           onupdate=db.func.timezone('UTC', db.func.current_timestamp()))
