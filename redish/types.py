from Queue import Empty, Full

from redish.utils import maybe_list, key


class Type(object):

    def __init__(self, name, client):
        self.name = key(name)
        self.client = client


class Counter(Type):

    def __init__(self, name, client, initial=None):
        super(Counter, self).__init__(name, client)
        if initial is not None:
            self.client.set(self.name, int(initial))

    def __iadd__(self, other):
        if other == 1:
            self.client.incr(self.name)
        else:
            self.client.incrby(self.name, other)

    def __isub__(self, other):
        if other == 1:
            self.client.decr(self.name)
        else:
            self.client.decrby(self.name, other)

    def __int__(self):
        return int(self.client.get(self.name))

    def __repr__(self):
        return repr(int(self))


class List(Type):

    def __init__(self, name, client, initial=None):
        super(List, self).__init__(name, client)
        self.extend(initial or [])

    def extend(self, iterable):
        for value in iterable:
            self.append(value)

    def extendleft(self, iterable):
        for value in iterable:
            self.appendleft(value)

    def __getitem__(self, index):
        return self.client.lindex(self.name, index)

    def __setitem__(self, index, value):
        return self.client.lset(self.name, index, value)

    def __len__(self):
        return self.client.llen(self.name)

    def _as_list(self):
        return self.client.lrange(self.name, 0, -1)

    def __repr__(self):
        return repr(self._as_list())

    def __iter__(self):
        return iter(self._as_list())

    def __getslice__(self, i, j):
        return self.client.lrange(self.name, i, j)

    def append(self, value):
        return self.client.rpush(self.name, value)

    def appendleft(self, value):
        return self.client.lpush(self.name, value)

    def trim(self, start, stop):
        return self.client.ltrim(self.name, start, stop)

    def pop(self):
        return self.client.rpop(self.name)

    def popleft(self):
        return self.client.lpop(self.name)

    def remove(self, value, count=1):
        count = self.client.lrem(self.name, value, num=count)
        if not count:
            raise ValueError("%s not in list" % value)
        return count


class Set(Type):

    def _as_set(self):
        return self.client.smembers(self.name)

    def __iter__(self):
        return iter(self._as_set())

    def __repr__(self):
        return repr(self._as_set())

    def __contains__(self, member):
        return self.client.sismember(self.name, member)

    def __len__(self):
        return self.client.scard(self.name)

    def add(self, member):
        return self.client.sadd(self.name, member)

    def remove(self, member):
        if not self.client.srem(self.name, member):
            raise KeyError(member)

    def pop(self):
        return self.client.spop(self.name)

    def union(self, others):
        return self.client.sunion(other.name for other in maybe_list(others))

    def union_update(self, others):
        return self.client.sunionstore(other.name
                                        for other in maybe_list(others))

    def intersection(self, others):
        return self.client.sinter(other.name for other in maybe_list(others))

    def intersection_update(self, others):
        return self.client.sinterstore(other.name
                                        for other in maybe_list(others))

    def difference(self, others):
        return self.client.sdiff(other.name for other in maybe_list(others))

    def difference_update(self, others):
        return self.client.sdiffstore(other.name
                                        for other in maybe_list(others))


class SortedSet(Type):

    def __getslice__(self, i, j):
        return self.client.zrange(self.name, i, j)

    def __len__(self):
        return self.client.zcard(self.name)

    def _as_set(self):
        return self.client.zrange(self.name, 0, -1)

    def __iter__(self):
        return iter(self._as_set())

    def __repr__(self):
        return repr(self._as_set())

    def add(self, member, score):
        return self.client.zadd(self.name, member, score)

    def remove(self, member):
        if not self.client.zrem(self.name, member):
            raise KeyError(member)


class Dict(Type):

    def __init__(self, name, client, initial=None, **extra):
        super(Dict, self).__init__(name, client)
        initial = dict(initial or {}, **extra)
        if initial:
            self.update(initial)

    def _setup(self, initial):
        if initial:
            self.update(initial)

    def __getitem__(self, key):
        value = self.client.hget(self.name, key)
        if value is not None:
            return value
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        return self.client.hset(self.name, key, value)

    def __contains__(self, key):
        return self.client.hexists(self.name, key)

    def __delitem__(self, key):
        if not self.client.hdel(self.name, key):
            raise KeyError(key)

    def __len__(self):
        return self.client.hlen(self.name)

    def keys(self):
        return self.client.hkeys(self.name)

    def values(self):
        return self.client.hvals(self.name)

    def _as_dict(self):
        return self.client.hgetall(self.name)

    def items(self):
        return self._as_dict().items()

    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return iter(self.values())

    def has_key(self, key):
        return key in self

    def get(self, key, failobj=None):
        try:
            return self[key]
        except KeyError:
            return failobj

    def setdefault(self, key, failobj=None):
        try:
            return self[key]
        except KeyError:
            self[key] = failobj
            return failobj

    def pop(self, key, failobj=None):
        try:
            val = self[key]
        except KeyError:
            val = failobj

        try:
            del(self[key])
        except KeyError:
            pass

        return val

    def update(self, other):
        return self.client.hmset(self.name, other)

    def __iter__(self):
        return iter(self.items())

    def __repr__(self):
        return repr(self._as_dict())

    def __cmp__(self, other):
        return cmp(self._as_dict(), other)

    def copy(self):
        return self._as_dict()


class Queue(Type):

    def __init__(self, name, client, initial=None, maxsize=0):
        super(Queue, self).__init__(name, client)
        self.list = List(name, client, initial)
        self.maxsize = maxsize
        self._pop = self.list.pop
        self._bpop = self.client.brpop
        self._append = self.list.appendleft

    def empty(self):
        return not len(self.list)

    def full(self):
        return self.maxsize and len(self.list) > self.maxsize

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()
        item = self._bpop(self.name, timeout=timeout)
        if item is not None:
            return item
        raise Empty

    def get_nowait(self):
        item = self._pop()
        if item is not None:
            return item
        raise Empty()

    def put(self, item):
        if self.full():
            raise Full()
        self._append(item)

    def qsize(self):
        return len(self.list)


class LIFOQueue(Queue):

    def __init__(self, name, client, initial=None, maxsize=0):
        super(LIFOQueue, self).__init__(name, client, initial, maxsize)
        self._pop = self.list.popleft
        self._bpop = self.client.blpop
