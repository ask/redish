import time
import uuid
from datetime import datetime

from redis import Redis as _RedisClient

from redish import types
from redish.serialization import Pickler

DEFAULT_PORT = 6379


class Client(object):
    host = "localhost"
    port = DEFAULT_PORT
    db = None
    serializer = Pickler()
    #serializer = anyjson

    def __init__(self, host=None, port=None, db=None):
        self.host = host or self.host
        self.port = port or self.port
        self.db = db or self.db
        self.api = _RedisClient(self.host, self.port, self.db)

    def List(self, name):
        return types.List(name=name, client=self.api)

    def SortedSet(self, name):
        return types.SortedSet(name=name, client=self.api)

    def Set(self, name):
        return types.Set(name=name, client=self.api)

    def prepare_value(self, value):
        return self.serializer.serialize(value)

    def value_to_python(self, value):
        return self.serializer.deserialize(value)

    def create_id(self):
        return str(uuid.uuid4())

    def dt_to_timestamp(self, dt):
        return time.mktime(dt.timetuple())

    def maybe_datetime(self, timestamp):
        if isinstance(timestamp, datetime):
            return self.dt_to_timestamp(timestamp)
        return timestamp

    def __getitem__(self, key):
        value = self.api.get(key)
        if value is None:
            raise KeyError(key)
        return self.value_to_python(value)

    def __setitem__(self, key, value):
        return self.api.set(key, self.prepare_value(value))

    def __delitem__(self, key):
        if not self.api.delete(key):
            raise KeyError(key)
