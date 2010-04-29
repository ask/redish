from redis import Redis as _RedisClient
from redis.exceptions import ResponseError

from redish import types
from redish.utils import mkey
from redish.serialization import Pickler

DEFAULT_PORT = 6379


class Client(object):
    """Redis Client

    :keyword host: Hostname of the Redis server to connect to.
        Default is ``"localhost"``.
    :keyword port: Port of the server to connect to.
        Default is ``6379``.
    :keyword db: Name of the database to use.
        Default is to use the default database.
    :keyword serializer: Object used to serialize/deserialize values.
        Must support the methods ``serialize(value)`` and
        ``deserialize(value)``. The default is to use
        :class:`redish.serialization.Pickler`.

    """

    host = "localhost"
    port = DEFAULT_PORT
    db = None
    serializer = Pickler()
    #serializer = anyjson

    def __init__(self, host=None, port=None, db=None,
            serializer=None):
        self.host = host or self.host
        self.port = port or self.port
        self.serializer = serializer or self.serializer
        self.db = db or self.db
        self.api = _RedisClient(self.host, self.port, self.db)

    def id(self, name):
        """Return the next id for a name."""
        return types.Id(name, self.api)

    def List(self, name, initial=None):
        """The list datatype.

        :param name: The name of the list.
        :keyword initial: Initial contents of the list.

        See :class:`redish.types.List`.

        """
        return types.List(name, self.api, initial=initial)

    def Set(self, name, initial=None):
        """The set datatype.

        :param name: The name of the set.
        :keyword initial: Initial members of the set.

        See :class:`redish.types.Set`.

        """
        return types.Set(name, self.api, initial)


    def SortedSet(self, name, initial=None):
        """The sorted set datatype.

        :param name: The name of the sorted set.
        :param initial: Initial members of the set as an iterable
           of ``(element, score)`` tuples.

        See :class:`redish.types.SortedSet`.

        """
        return types.SortedSet(name, self.api, initial)

    def Dict(self, name, initial=None, **extra):
        """The dictionary datatype (Hash).

        :param name: The name of the dictionary.
        :keyword initial: Initial contents.
        :keyword \*\*extra: Initial contents as keyword arguments.

        The ``initial``, and ``**extra`` keyword arguments
        will be merged (keyword arguments has priority).

        See :class:`redish.types.Dict`.

        """
        return types.Dict(name, self.api, initial=initial, **extra)

    def Queue(self, name, initial=None, maxsize=None):
        """The queue datatype.

        :param name: The name of the queue.
        :keyword initial: Initial items in the queue.

        See :class:`redish.types.Queue`.

        """
        return types.Queue(name, self.api, initial=initial, maxsize=maxsize)

    def LifoQueue(self, name, initial=None, maxsize=None):
        """The LIFO queue datatype.

        :param name: The name of the queue.
        :keyword initial: Initial items in the queue.

        See :class:`redish.types.LifoQueue`.

        """
        return types.LifoQueue(name, self.api,
                               initial=initial, maxsize=maxsize)

    def prepare_value(self, value):
        """Encode python object to be stored in the database."""
        return self.serializer.encode(value)

    def value_to_python(self, value):
        """Decode value to a Python object."""
        return self.serializer.decode(value)

    def clear(self):
        """Remove all keys from the current database."""
        return self.api.flushdb()

    def update(self, mapping):
        """Update database with the key/values from a :class:`dict`."""
        return self.api.mset(dict((key, self.prepare_value(value))
                                for key, value in mapping.items()))

    def rename(self, old_name, new_name):
        """Rename key to a new name."""
        try:
            self.api.rename(mkey(old_name), mkey(new_name))
        except ResponseError, exc:
            if "no such key" in exc.args:
                raise KeyError(old_name)
            raise

    def keys(self, pattern="*"):
        """Get a list of all the keys in the database, or
        matching ``pattern``."""
        return self.api.keys(pattern)

    def iterkeys(self, pattern="*"):
        """An iterator over all the keys in the database, or matching
        ``pattern``."""
        return iter(self.keys(pattern))

    def iteritems(self, pattern="*"):
        """An iterator over all the ``(key, value)`` items in the database,
        or where the keys matches ``pattern``."""
        for key in self.keys(pattern):
            yield (key, self[key])

    def items(self, pattern="*"):
        """Get a list of all the ``(key, value)`` pairs in the database,
        or the keys matching ``pattern``, as 2-tuples."""
        return list(self.iteritems(pattern))

    def itervalues(self, pattern="*"):
        """Iterate over all the values in the database, or those where the
        keys matches ``pattern``."""
        for key, value in self.iteritems(pattern):
            yield value

    def values(self, pattern="*"):
        """Get a list of all values in the database, or those where the
        keys matches ``pattern``."""
        return list(self.itervalues(pattern))

    def pop(self, name):
        """Get and remove key from database (atomic)."""
        name = mkey(name)
        temp = mkey((name, "__poptmp__"))
        self.rename(name, temp)
        value = self[temp]
        del(self[temp])
        return value

    def get(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise returns
        ``default`` (``None`` by default.)"""
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, name):
        """``x.__getitem__(name) <==> x[name]``"""
        name = mkey(name)
        value = self.api.get(name)
        if value is None:
            raise KeyError(name)
        return self.value_to_python(value)

    def __setitem__(self, name, value):
        """``x.__setitem(name, value) <==> x[name] = value``"""
        return self.api.set(mkey(name), self.prepare_value(value))

    def __delitem__(self, name):
        """``x.__delitem__(name) <==> del(x[name])``"""
        name = mkey(name)
        if not self.api.delete(name):
            raise KeyError(name)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.api.dbsize()

    def __contains__(self, name):
        """``x.__contains__(name) <==> name in x``"""
        return self.api.exists(mkey(name))

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return "<RedisClient: %s:%s/%s>" % (self.host,
                                           self.port,
                                           self.db or "")
