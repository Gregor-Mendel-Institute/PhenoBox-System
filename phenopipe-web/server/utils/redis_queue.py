class RedisQueue(object):
    def __init__(self, connection, name, namespace='queue'):
        """
        Initializes the queue and computes the according redis key which looks like the following 'namespace:name'.
        :param connection: The connection to Redis to be used by the queue
        :param name: The name of the queue. Used in the redis key
        :param namespace: The namespace where this queue will be located in redis
        """
        self._connection = connection
        self._key = '{namespace}:{name}'.format(namespace=namespace, name=name)

    def enqueue(self, item):
        """
        Puts the given serialized object and inserts it at the end of the queue
        :param item: The serialized object to be enqueued
        :return: None
        """
        self._connection.lpush(self._key, item)

    def peek(self):
        return self._connection.lrange(self._key, -1, -1)

    def dequeue(self, block=True, timeout=None):
        """
        Gets the next object from the queue and returns it. By default this is a blocking operation but one can specify
        a timeout or prevent blocking at all.

        In non-blocking mode it will throw an :class:`Empty` exception if there is no item available.

        :param block: Boolean value to represent whether this method should block until an item is available. Default: True
        :param timeout: Value to specify how long it should block and wait for a new object. Default: None

        :raises Empty: if no item was in the queue at the time of reading if block is False or if no item was found
            until timeout period was over if block was True

        :return: The dequeued item.
        """
        if block:
            item = self._connection.brpop(self._key, timeout=timeout)
        else:
            item = self._connection.rpop(self._key)

        if item:
            item = item[1]
        if item is None:
            raise Empty("Queue '{key}' is empty".format(key=self._key))
        return item

    def requeue(self, item):
        """
        Insert the given serialized item at the front of the queue

        :param item: The serialized object to be enqueued

        :return: None
        """
        self._connection.rpush(self._key, item)


class Empty(Exception):
    pass
