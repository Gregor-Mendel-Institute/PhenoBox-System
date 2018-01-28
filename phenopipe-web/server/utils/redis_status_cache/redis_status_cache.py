import base64
import time
from threading import RLock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rq import Queue

from server.utils.redis_status_cache.redis_status_log import StatusLog
from server.utils.redis_status_cache.status_object import StatusObject

"""
This module is used to store status information for background jobs for a specific RQ Queue. 
This class is intended to be used as a Singleton
"""


class StatusCache():
    def __init__(self, connection, namespace, ttl=2880, rq_queue_name=''):
        """
        Initializes the Status cache with a redis connection and the according namespace which it will use for its keys
        inside Redis. The cache will remove items if they are stored for longer than ttl which is given in minutes.

        :param connection: The redis connection which is used by the cache
        :param namespace: The top level key which will be used inside redis
        :param ttl: The time to live (in minutes) after which entries will expire and be removed from the cache
        :param rq_queue_name: The name of the RQ Queue. By default it is the same as namespace.
        """
        self._connection = connection
        self._namespace = namespace
        if rq_queue_name == '':
            self._rq_queue_name = namespace
        self._log_store = StatusLog(connection, namespace + ':log')
        self._queue = Queue(self._rq_queue_name, connection=connection)
        self._lock = RLock()
        self._ttl = ttl
        if ttl != -1:
            pass
            #TODO reenable scheduler
            #self._eviction_scheduler = BackgroundScheduler()
            # self._eviction_scheduler.add_job(self._evict, trigger=IntervalTrigger(minutes=ttl))
            # TODO remove
            #self._eviction_scheduler.add_job(self._evict, trigger=IntervalTrigger(minutes=2))
            # self._ttl = 2
            # self._eviction_scheduler.start()

    @staticmethod
    def generate_id(*args):
        """
        Generate an id by concatenating all arguments with ':' as the delimiter and base64 encode the result

        :param args: Arbitrary number of string arguments, which should uniquely identify an object

        :return: a base64 encoded id
        """
        s = ''
        first = True
        for arg in args:
            if not first:
                s += ':'
            else:
                first = False
            s += arg
        return base64.b64encode(s)

    @staticmethod
    def from_id(status_id):
        """
        decodes the given id into its parts which were delimited by ':'

        :param status_id: the id to be decoded

        :return: a list of the different parts of the id
        """
        id_string = base64.b64decode(status_id)
        return id_string.split(':')

    def _evict_job(self, job_id):
        """
        Deletes the job with the given id from the RQ

        :param job_id: The unique id of the job which should be deleted

        :return: None
        """
        job = self._queue.fetch_job(job_id)
        if job is not None:
            job.delete()

    def _evict_hash(self, key):
        """
        Gets the Status object stored at the given key, removes all the corresponding jobs and deletes the entry itself
        :param key: The key to the status hash which should be deleted

        :return: None
        """
        job_ids = StatusObject.load_field(self._connection.hget(key, StatusObject.job_ids_key),
                                          StatusObject.job_ids_key)
        print(job_ids)
        for job_id in job_ids.values():
            self._evict_job(job_id)
        self._connection.delete(key)

    def _evict(self):
        """
        Gets jobs which have been stored for longer than ttl and removes them from the cache

        :return: None
        """
        print('eviction triggered')
        identifiers = self._connection.sscan_iter(self._namespace)
        ts = time.time()
        for identifier in identifiers:
            obsolete = self._connection.zrangebyscore(self._get_zset_key(identifier), 0, ts - self._ttl * 60)
            for key in obsolete:
                self._evict_hash(self._get_hash_key(identifier, key))
                self._log_store.delete_log(key)
            self._connection.zremrangebyscore(self._get_zset_key(identifier), 0, ts - self._ttl * 60)
            if not self._connection.exists(self._get_zset_key(identifier)):
                self._connection.srem(self._namespace, identifier)

    def _get_zset_key(self, identifier):
        """
        Constructs the key for the scored set which is used to reference all status objects for a specific identifier

        :param identifier:

        :return: The full redis key for the scored set
        """
        return '{}:{}'.format(self._namespace, identifier)

    def _get_hash_key(self, identifier, status_id):
        """
         Constructs the key for the status hash which is used to store the status information
        :param identifier:
        :param status_id: The id of the status hash
        :return: The full redis key for the status hash
        """
        return '{}:{}:{}'.format(self._namespace, identifier, status_id)

    def put(self, identifier, status_obj):
        """
        Insert a status object into Redis and delete old logs if there are any.

        First the identifier is stored in the top level to make iteration over all status hashes easier.
        Additionally the status id is stored in a scored set which belongs to the identifier where the current time is as the score.
        The status object itself is serialized and stored as a hash

        :param identifier: A string representing a specific entity (e.g. a user)

        :param status_obj: The :class:`.StatusObject` to be stored

        :return: None
        """
        self._lock.acquire()
        try:
            self._log_store.delete_log(status_obj.id)
            self._connection.sadd(self._namespace, identifier)
            self._connection.zadd(self._get_zset_key(identifier), time.time(), status_obj.id)
            self._connection.hmset(self._get_hash_key(identifier, status_obj.id), status_obj.serialize())
        finally:
            self._lock.release()

    def update(self, identifier, status_obj):
        """
        Replaces the currently stored object in the hash with the given status obj

        :param identifier:
        :param status_obj: The :class:`.StatusObject` to be serialized and stored

        :return: None
        """
        # TODO check if item is already present
        key = self._get_hash_key(identifier, status_obj.id)
        if self._connection.exists(key):
            self._connection.hmset(key, status_obj.serialize())
        else:
            raise KeyError('There is no object for this key. Please insert before trying to update')

    def get(self, identifier, status_id):
        """
        Fetch the hash for the given id from redis and deserialize the status object

        :param identifier:
        :param status_id: the ID for the status hash

        :return: the loaded instance of :class:`.StatusObject`
        """
        # TODO respect TTL
        h = self._connection.hgetall(self._get_hash_key(identifier, status_id))
        if h == {}:
            return None
        return StatusObject.load(h)

    def get_all(self, identifier):
        """
        Returns a list of all hash IDs which are stored (and not already expired) for the given identifier

        :param identifier:

        :return: List of status IDs
        """
        ts = time.time()
        return self._connection.zrangebyscore(self._get_zset_key(identifier), ts - self._ttl * 60, ts)

    def get_all_identifiers(self):
        """
        Retruns a list of all identifiers which are currently present in this cache

        :return: List of identifier keys
        """
        return self._connection.sscan_iter(self._namespace)

    def checked_put(self, identifier, status_obj):
        """
        Only puts the :class:`.StatusObject` into the cache if it is not already present or if the existing one is in
        the error state.

        :param identifier:
        :param status_obj: The :class:`.StatusObject` to be serialized and stored

        :return: True if the object has been put into the cache. False otherwise.
        """
        self._lock.acquire()
        try:
            curr_status = self.get(identifier, status_obj.id)
            if not curr_status or curr_status.has_error():
                self.put(identifier, status_obj)
                return True
            return False
        finally:
            self._lock.release()

    def log(self, status_id, message, progress=0):
        print(message)
        self._log_store.put(status_id, message, progress)

    def log_all(self, status_id, messages, progress):
        if len(messages) != len(progress):
            # TODO Raise exception
            return
        self._log_store.put_all(status_id, messages, progress)

    def get_last_n_logs(self, status_id, n):
        # TODO respect TTL
        return self._log_store.get_last_n(status_id, n)

    def get_full_log(self, status_id, reverse=False):
        """
        Returns the log for the given status_id from the oldest to the newest message if reverse is False and from newest
        to oldest if reverse is true

        :param status_id:
        :param reverse:

        :return:
        """
        # TODO respect TTL
        if reverse:
            return reversed(self._log_store.get_all(status_id))
        return self._log_store.get_all(status_id)
