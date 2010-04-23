try:
    import cPickle as pickle
except ImportError:
    import pickle


class Pickler(object):
    protocol = 2

    def serialize(self, value):
        return pickle.dumps(value, protocol=self.protocol)

    def deserialize(self, value):
        return pickle.loads(value)
