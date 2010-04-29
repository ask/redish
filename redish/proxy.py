#!/usr/bin/env python
# encoding: utf-8
"""
proxy.py

Created by Adam T. Lindsay on 2010-04-28.

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

def int_or_str(thing, key, client):
    try:
        int(thing)
        return types.Int(key, client)
    except (TypeError, ValueError):
        return decode(thing, "UTF-8")

class Proxy(Redis):
    def __getitem__(self, key):
        typ = self.type(key)
        if typ == 'none':
            raise KeyError(key)
        elif typ == 'string':
            return int_or_str(self.get(key), key, self)
        else:
            return TYPE_MAP[typ](key, self)
    
    def __setitem__(self, key, value):
        if isinstance(value, (int, types.Int)):
            self.set(key, int(value))
            return
        elif isinstance(value, basestring):
            self.set(key, encode(value, "UTF-8"))
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
        pline.execute()
    
