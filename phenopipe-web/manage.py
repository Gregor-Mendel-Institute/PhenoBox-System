from flask_migrate import MigrateCommand
from flask_script import Manager

from server import create_app
from server.cli import db_manager

manager = Manager(create_app)
manager.add_option('-c', '--config',
                   dest="configname",
                   required=True,
                   help="Config file")

manager.add_command('alembic', MigrateCommand)
manager.add_command('db', db_manager)

if __name__ == '__main__':
    manager.run()
