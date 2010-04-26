import time
import uuid
from datetime import datetime

from redis import Redis as _RedisClient

from redish import types
from redish.utils import key
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

    def List(self, name, initial=None):
        return types.List(name, self.api, initial=initial)

    def SortedSet(self, name):
        return types.SortedSet(name, self.api)

    def Set(self, name):
        return types.Set(name, self.api)

    def Dict(self, name, initial=None, **extra):
        return types.Dict(name, self.api, initial=initial, **extra)

    def Counter(self, name, initial=None):
        return types.Counter(name, self.api, initial=initial)

    def Queue(self, name, initial=None):
        return types.Queue(name, self.api, initial=initial)

    def LIFOQueue(self, name, initial=None):
        return types.LIFOQueue(name, self.api, initial=initial)

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

    def __getitem__(self, name):
        name = key(name)
        value = self.api.get(name)
        if value is None:
            raise KeyError(name)
        return self.value_to_python(value)

    def __setitem__(self, name, value):
        return self.api.set(key(name), self.prepare_value(value))

    def __delitem__(self, name):
        name = key(name)
        if not self.api.delete(name):
            raise KeyError(name)

    def __len__(self):
        return self.api.dbsize()

    def __contains__(self, name):
        return self.api.exists(key(name))

    def clear(self):
        return self.api.flushdb()

    def update(self, mapping):
        return self.api.mset(mapping)
