import os
import signal
import sys

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import jwt_required

from extensions import db, jwt, migrate
from server.api import api
from server.api.graphql.custom_graphql_view import CustomGraphQLView
from server.auth import authentication
from server.auth.box_authenticator import BoxAuthenticator
from server.auth.dummy_authenticator import DummyAuthenticator
from server.auth.endpoints import auth
from server.auth.gmi_authenticator import GMIAuthenticator
from server.modules.analysis.result_handler import ResultHandler
from server.modules.printer.printer import Printer
from .api import schema

printer = None
server_app = None
analysis_result_handler = None


def exit_handler(signal, frame):
    """
    Registered as a handler to SIGINT to shut down all parts of the application properly
    :param signal:
    :param frame:
    :return:
    """
    print 'exit'
    global server_app
    server_app.logger.info('Initiated Shutdown')
    if printer is not None:
        printer.stop()
        printer.join()
    if analysis_result_handler is not None:
        analysis_result_handler.stop()
        analysis_result_handler.join()

    sys.exit(0)


def configure_extensions(app):
    cors = CORS(app)
    jwt.init_app(app)
    # cors.init_app(app)

    db.init_app(app)

    migrate.init_app(app, db)
    global printer
    printer = Printer(app.config['PRINTER_IP'], app.config['PRINTER_PORT'])
    printer.setDaemon(True)
    printer.start()
    #global analysis_result_handler
    #analysis_result_handler = ResultHandler()
    #analysis_result_handler.setDaemon(True)
    #analysis_result_handler.start()


def configure_logging(app):
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = RotatingFileHandler('server.log', maxBytes=5242880,
                                           backupCount=4)  # TODO set absolute path in config
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)


def create_app(configname='default_config', app_name=None, modules=None):
    print 'start server'

    app = Flask(__name__, static_folder='./static', template_folder='templates')
    print 'config name: ', configname
    app.config.from_pyfile(os.path.join('config', configname + '.py'))
    global server_app
    server_app = app
    configure_logging(app)
    configure_extensions(app)
    if not app.config['PRODUCTION']:
        authentication.register_authenticator(DummyAuthenticator())
    authentication.register_authenticator(GMIAuthenticator())
    authentication.register_authenticator(BoxAuthenticator())

    app.register_blueprint(api)
    app.register_blueprint(auth)

    graphql_sec_view = jwt_required(CustomGraphQLView.as_view('graphql', schema=schema, graphiql=False))
    app.add_url_rule('/graphql', view_func=graphql_sec_view)
    if not app.config['PRODUCTION']:
        graphql_view = CustomGraphQLView.as_view('graphql_insec', schema=schema, graphiql=True)
        app.add_url_rule('/graphql_insec', view_func=graphql_view)

    server_app = app
    signal.signal(signal.SIGINT, exit_handler)
    app.logger.info('Server Created')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
