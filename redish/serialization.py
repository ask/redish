try:
    import cPickle as pickle
except ImportError:
    import pickle

import anyjson

from redish.utils import maybe_list


class Serializer(object):

    def __init__(self, encoding=None):
        self.encoding = encoding

    def encode(self, value):
        value = self.serialize(value)
        if self.encoding:
            value = value.encode(self.encoding)
        return value

    def decode(self, value):
        if self.encoding:
            value = value.decode(self.encoding)
        return self.deserialize(value)


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
        return anyjson.serialize(value)

    def deserialize(self, value):
        return anyjson.deserialize(value)
