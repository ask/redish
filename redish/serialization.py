try:
    import cPickle as pickle
except ImportError:
    import pickle

import anyjson

from redish.utils import maybe_list


class Serializer(object):
    """Base class for serializers.

    :keyword encoding: Optional encoding applied after serialization,
        and before deserialization.

    Example using compression::

        >>> s = Pickler(encoding="zlib")
        >>> val = s.encode({"foo: "bar"})
        >>> s.decode(val)

    Serializers must implement the :meth:`serialize` and :meth:`deserialize`
    methods. Both take a single argument, which is the value to
    serialize/deserialize.

    """

    def __init__(self, encoding=None):
        self.encoding = encoding

    def encode(self, value):
        """Encode value."""
        value = self.serialize(value)
        if self.encoding:
            value = value.encode(self.encoding)
        return value

    def decode(self, value):
        """Decode value."""
        if self.encoding:
            value = value.decode(self.encoding)
        return self.deserialize(value)

    def serialize(self, value):
        raise NotImplementedError("Serializers must implement serialize()")

    def deserialize(self, value):
        raise NotImplementedError("Serializers must implement deserialize()")


class Plain(Serializer):
    """A pass-through serializer.

    Values will not be serialized.

    """

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class Pickler(Serializer):
    """The :mod:`pickle` serializer."""
    protocol = 2

    def serialize(self, value):
        """Encode value to pickle format."""
        return pickle.dumps(value, protocol=self.protocol)

    def deserialize(self, value):
        """Decode pickled value to Python object."""
        return pickle.loads(value)


class JSON(Serializer):

    def serialize(self, value):
        """Encode value to JSON format."""
        return anyjson.serialize(value)

    def deserialize(self, value):
        """Decode JSON to Python object."""
        return anyjson.deserialize(value)
