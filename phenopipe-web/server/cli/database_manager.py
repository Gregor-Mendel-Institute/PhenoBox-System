from flask_script import Manager
from flask_script import prompt_bool

from server.extensions import db

manager = Manager(usage="Perform commands on the database back-end")


@manager.command
def drop(force=False):
    """
    Drop all database tables
    """
    if force or prompt_bool("Are you sure you want to drop all the database tables?"):
        db.drop_all()
        return True

    return False


@manager.command
def create(empty=False):
    """
    Creates database tables for the application models and loads the seed data
    """
    db.create_all()
