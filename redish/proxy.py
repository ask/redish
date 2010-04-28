#!/usr/bin/env python
# encoding: utf-8
"""
proxy.py

Created by Adam T. Lindsay on 2010-04-28.

"""
from redis import Redis
from redish import types, client

TYPE_MAP = {
    "list":   types.List,
    "set":    types.Set,
    "zset":   types.SortedSet,
    "hash":   types.Dict,
}

def int_or_str(thing):
    try:
        return int(thing)
    except (TypeError, ValueError):
        return thing

class Proxy(Redis):
    def __getitem__(self, key):
        typ = self.type(key)
        if typ == 'none':
            raise KeyError(key)
        elif typ == 'string':
            return int_or_str(self.get(key))
        else:
            return TYPE_MAP[typ](key, self)
    
    def __setitem__(self, key, value):
        if isinstance(value, (int, basestring)):
            self.set(key, value)
            return
        pline = self.pipeline()
        if self.exists(key):
            pline = pline.delete(key)
        if isinstance(value, list):
            for item in value:
                pline = pline.rpush(key, item)
        elif isinstance(value, set):
            for item in value:
                pline = pline.sadd(key, item)
        elif isinstance(value, dict):
            pline = pline.hmset(key, value)
        pline.execute()
