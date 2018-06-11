import json
from datetime import datetime


class LogStore(object):
    def __init__(self, connection, namespace):
        self._connection = connection
        self._namespace = namespace

    def _get_list_key(self, id):
        return '{}:{}'.format(self._namespace, id)

    def _get_log_range(self, id, start, end):
        entries = self._connection.lrange(self._get_list_key(id), start, end)
        items = []
        for entry in entries:
            item = json.loads(entry)
            items.append((item['t'], item['m'], item['p']))
        return items

    def delete_log(self, id):
        self._connection.delete(self._get_list_key(id))

    def put(self, id, message, progress=0):
        item = json.dumps({'t': datetime.utcnow().isoformat(), 'm': message, 'p': progress})
        self._connection.rpush(self._get_list_key(id), item)

    def put_all(self, id, messages, progress):
        for i in range(0, len(messages)):
            self.put(id, messages[i], progress[i])

    def get_all(self, id, reverse=False):
        if reverse:
            return reversed(self._get_log_range(id, 0, -1))
        return self._get_log_range(id, 0, -1)

    def get_last_n(self, id, n):
        return self._get_log_range(id, -n, -1)
