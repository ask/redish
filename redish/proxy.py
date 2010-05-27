"""
.. module:: proxy.py
   :synopsis: Transparent access to Redis as a data structure server
.. moduleauthor:: Adam T. Lindsay <http://github.com/atl>

Rather than use the native redis-py's methods for getitem/setitem as simple
key-value storage, use item access as a means to obtain proxy objects for
structures in the redis store. The proxy objects are obtained from
redish.types -- no other redish modules are used.

This provides as simple access as possible to Redis as a "data structure"
server.

(originally by Adam T. Lindsay)
"""
from codecs import encode, decode
from redis import Redis
from redish import types

TYPE_MAP = {
    "list":   types.List,
    "set":    types.Set,
    "zset":   types.SortedSet,
    "hash":   types.Dict,
}

REV_TYPE_MAP = {
    list:       types.List,
    set:        types.Set,
    dict:       types.Dict,
    types.ZSet: types.SortedSet,
}

def int_or_str(thing, key, client):
    try:
        int(thing)
        return types.Int(key, client)
    except (TypeError, ValueError):
        return decode(thing, "UTF-8")

class Proxy(Redis):
    """Acts as the Redis object except with basic item access or assignment.
    In those cases, transparently returns an object that mimics its 
    associated Python type or passes assignments to the backing store."""
    
    def __init__(self, **kwargs):
        """
        The `miss` argument accepts a function of one argument to which 
        it passes a key, if the key is unknown in the datastore. By default
        it returns a "None". Another possibility for more strict checking 
        is passing in a KeyError. If a user attempts to initialize a redis 
        key with an empty container, that container is kept in the (local
        threading) proxy object so that subsequent accesses keep the 
        right type without throwing KeyErrors.
        """
        try:
            self.miss = kwargs.pop('miss')
        except KeyError:
            self.miss = lambda x: None
        self.empties = {}
        super(Proxy, self).__init__(**kwargs)
    
    def __getitem__(self, key):
        """Return a proxy type according to the native redis type 
        associated with the key."""
        typ = self.type(key)
        if typ == 'none':
            if key in self.empties:
                return self.empties[key]
            result = self.miss(key)
            if isinstance(result, Exception):
                raise result
            else:
                return result
        elif typ == 'string':
            return int_or_str(self.get(key), key, self)
        else:
            return TYPE_MAP[typ](key, self)
    
    def __setitem__(self, key, value):
        """Copy the contents of the value into the redis store."""
        if isinstance(value, (int, types.Int)):
            self.set(key, int(value))
            return
        elif isinstance(value, basestring):
            self.set(key, encode(value, "UTF-8"))
            return
        if not value and value != None:
            self.empties[key] = REV_TYPE_MAP[type(value)](key, self)
        elif value and key in self.empties:
            self.empties.pop(key)
        pline = self.pipeline()
        if self.exists(key):
            pline = pline.delete(key)
        if isinstance(value, (list, types.List)):
            for item in value:
                pline = pline.rpush(key, item)
        elif isinstance(value, (set, types.Set)):
            for item in value:
                pline = pline.sadd(key, item)
        elif isinstance(value, (dict, types.Dict)):
            pline = pline.hmset(key, value)
        elif isinstance(value, (types.ZSet, types.SortedSet)):
            for k,v in value.items():
                pline = pline.zadd(key, k, v)
        pline.execute()
    
    def __contains__(self, key):
        return self.exists(key) or key in self.empties
    
