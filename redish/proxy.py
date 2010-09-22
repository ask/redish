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
import re
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

# OMG, what have I done?
FORMAT_SPEC = re.compile(r'%(\(\w+\))?[#0\- \+]?[0-9\*]*\.?[0-9\*]*[hlL]?[diouxXeXfXgGcrs]')

def int_or_str(thing, key, client):
    try:
        int(thing)
        return types.Int(key, client)
    except (TypeError, ValueError):
        return decode(thing, "UTF-8")

class Glob(str):
    pass

class Proxy(Redis):
    """Acts as the Redis object except with basic item access or assignment.
    In those cases, transparently returns an object that mimics its 
    associated Python type or passes assignments to the backing store."""
    
    def __init__(self, *args, **kwargs):
        """
        This mostly defers to the main redis-py object, with the exception of 
        keeping track of empty elements and keyspaces.
        
        If a user attempts to initialize a redis key with an empty container, 
        that container is kept in the (local thread's) proxy object so that 
        subsequent accesses keep the right type without throwing KeyErrors.
        """
        self._empties = {}
        self._keyspaces = {}
        super(Proxy, self).__init__(*args, **kwargs)
    
    def keyspaced(f):
        def preprocessed(self, key, *argv):
            if isinstance(key, tuple):
                keyspace = key[0]
                if len(key) == 2:
                    keyargs = key[1:][0]
                else:
                    keyargs = tuple(key[1:])
                key = self._keyspaces[keyspace] % keyargs
            return f(self, key, *argv)
        preprocessed.__doc__ = f.__doc__
        preprocessed.__name__ = f.__name__
        return preprocessed
    
    @keyspaced
    def __getitem__(self, key):
        """Return a proxy type according to the native redis type 
        associated with the key."""
        if isinstance(key, Glob):
            return self.multikey(key)
        typ = self.type(key)
        if typ == 'string':
            # because strings can be empty, check before "empties"
            return int_or_str(self.get(key), key, self)
        if key in self._empties:
            if typ == 'none':
                return self._empties[key]
            else:
                self._empties.pop(key)
        if typ == 'none':
            raise KeyError(key)
        else:
            return TYPE_MAP[typ](key, self)
    
    @keyspaced
    def __setitem__(self, key, value):
        """Copy the contents of the value into the redis store."""
        if key in self._empties:
            del self._empties[key]
        if isinstance(value, (int, types.Int)):
            self.set(key, int(value))
            return
        elif isinstance(value, basestring):
            self.set(key, encode(value, "UTF-8"))
            return
        if not value:
            if self.exists(key):
                self.delete(key)
            if value != None:
                self._empties[key] = REV_TYPE_MAP[type(value)](key, self)
            return
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
    
    @keyspaced
    def __contains__(self, key):
        """
        We check for existence within the *proxy object*, and so we
        must look in both the backing store and the object's "empties."
        """
        return self.exists(key) or key in self._empties
    
    @keyspaced
    def __delitem__(self, k):
        if isinstance(k, Glob):
            keys = self.keys(k)
        else:
            keys = [k]
        for key in keys:
            if key in self._empties:
                del self._empties[key]
        self.delete(*keys)
    
    def values(self, pattern):
        if pattern in self._keyspaces:
            pattern = FORMAT_SPEC.sub('*', self._keyspaces[pattern])
        return [self[p] for p in super(Proxy, self).keys(pattern)]
    
    def keys(self, pattern):
        if pattern in self._keyspaces:
            pattern = FORMAT_SPEC.sub('*', self._keyspaces[pattern])
        return super(Proxy, self).keys(pattern)
    
    def items(self, pattern):
        if pattern in self._keyspaces:
            pattern = FORMAT_SPEC.sub('*', self._keyspaces[pattern])
        return [(p, self[p]) for p in super(Proxy, self).keys(pattern)]
    
    def register_keyspace(self, shortcut, formatstring):
        """
        Define a keyspace by mapping a label to a formatstring.
        
        The function returns the name of the shortcut to facilitate
        symbolic access with this pattern::
        
            VALUE = proxyobject.register_keyspace('val', "user:%d:name")
        
        The following three statements are then all equivalent::
        
            proxyobject[VALUE, 1001] = "Fred"
            proxyobject['val', 1001] = "Fred"
            proxyobject['user:1001:name'] = "Fred"
        """
        self._keyspaces[shortcut] = formatstring
        return shortcut
    
    def keyspace(self, keyspace):
        """
        Convenient, consistent access to a sub-set of all keys.
        """
        if FORMAT_SPEC.search(keyspace):
            return KeyspacedProxy(self, keyspace)
        else:
            return KeyspacedProxy(self, self._keyspaces[keyspace])
    
    @keyspaced
    def actual_key(self, key):
        """
        For debugging.
        """
        return key
    

class KeyspacedProxy(Proxy):
    """
    The easiest way of describing this is that it simulates a partial on the 
    mapping object by interpolating the keyspace. Clear?
    """
    def __init__(self, proxy, transform):
        self.proxy = proxy
        self.transform = transform
        self.globbed = FORMAT_SPEC.sub('*', transform)
    
    def __getitem__(self, key):
        return self.proxy.__getitem__(self.transform % key)
    
    def __setitem__(self, key, value):
        return self.proxy.__setitem__(self.transform % key, value)
    
    def __contains__(self, key):
        return self.proxy.__contains__(self.transform % key)
    
    def __delitem__(self, key):
        return self.proxy.__delitem__(self.transform % key)
    
    def keys(self):
        return self.proxy.keys(self.globbed)
    
    def values(self):
        return self.proxy.values(self.globbed)
    
    def items(self):
        return self.proxy.items(self.globbed)
    
