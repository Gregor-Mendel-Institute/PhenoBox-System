# FIXME Cleaner config setup!! Don't use Flask Config loader?

import grpc
import redis
from flask import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.utils.redis_log_store import LogStore
from server.utils.util import static_vars

"""
Module to let Jobs access various globally initialized objects
"""


@static_vars(cfg=None)
def get_config(path=None, filename=None):
    """
    Used to make the config globally accessible for jobs
    Has to be accessed once with a path and config filename.
    After that it will return the same object everytime without the need to pass a path or a filename

    :param path: The path to the containing folder of the config file
    :param filename: The filename of the config file (Needs to be a .py file)
    :return: The loaded :class:`~flask.Config` instance
    """
    if get_config.cfg is None and path is not None and filename is not None:
        cfg = Config(path)
        cfg.from_pyfile(filename=filename)
        get_config.cfg = cfg
    return get_config.cfg


@static_vars(channel=None)
def get_grpc_channel():
    """
    Lazily initialized GRPC channel to the Analysis/IAP Server

    :return: Instance of a :class:`grpc.Channel`
    """
    if get_grpc_channel.channel is None:
        grpc_ip = get_config()['ANALYSIS_SERVER_IP']
        grpc_port = get_config()['ANALYSIS_SERVER_GRPC_PORT']
        get_grpc_channel.channel = grpc.insecure_channel('{}:{}'.format(grpc_ip, str(grpc_port)))
    return get_grpc_channel.channel


@static_vars(connection=None)
def get_redis_connection():
    """
    Lazily initialized Redis connection

    :return: Redis connection object
    """
    if get_redis_connection.connection is None:
        get_redis_connection.connection = redis.StrictRedis(host=get_config()['REDIS_IP'],
                                                            port=get_config()['REDIS_PORT'], db=0)
    return get_redis_connection.connection


@static_vars(log_store=None)
def get_log_store():
    """
    Lazily initialized instance of :class:`~server.utils.redis_status_log.LogStore` for analysis jobs

    :return: Instance of :class:`~server.utils.redis_status_log.LogStore`
    """
    if get_log_store.log_store is None:
        get_log_store.log_store = LogStore(connection=get_redis_connection(), namespace='tasks:logs')
    return get_log_store.log_store


@static_vars(Session=None)
def get_session():
    """
    Lazily initializes a SQLAlchemy sessionmaker

    :return: A new SQLAlchemy session instance
    """
    if get_session.Session is None:
        engine = create_engine(get_config()['SQLALCHEMY_DATABASE_URI'])
        get_session.Session = sessionmaker(bind=engine)
    return get_session.Session()
