from Queue import Empty, Full

from redis.exceptions import ResponseError

from redish.utils import mkey


class Type(object):
    """Base-class for Redis datatypes."""

    def __init__(self, name, client):
        self.name = mkey(name)
        self.client = client


def Id(name, client):
    """Return the next value for an unique id."""
    return "%s:%s" % (name, client.incr("ids:%s" % (name, )), )


class List(Type):
    """A list."""

    def __init__(self, name, client, initial=None):
        super(List, self).__init__(name, client)
        self.extend(initial or [])

    def __getitem__(self, index):
        """``x.__getitem__(index) <==> x[index]``"""
        item = self.client.lindex(self.name, index)
        if item:
            return item
        raise IndexError("list index out of range")

    def __setitem__(self, index, value):
        """``x.__setitem__(index, value) <==> x[index] = value``"""
        try:
            self.client.lset(self.name, index, value)
        except ResponseError, exc:
            if "index out of range" in exc.args:
                raise IndexError("list assignment index out of range")
            raise

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.llen(self.name)

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_list())

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_list())

    def __getslice__(self, i, j):
        """``x.__getslice__(start, stop) <==> x[start:stop]``"""
        # Redis indices are zero-based, while Python indices are 1-based.
        return self.client.lrange(self.name, i, j - 1)

    def _as_list(self):
        return self.client.lrange(self.name, 0, -1)

    def append(self, value):
        """Add ``value`` to the end of the list."""
        return self.client.rpush(self.name, value)

    def appendleft(self, value):
        """Add ``value`` to the head of the list."""
        return self.client.lpush(self.name, value)

    def trim(self, start, stop):
        """Trim the list to the specified range of elements."""
        return self.client.ltrim(self.name, start, stop - 1)

    def pop(self):
        """Remove and return the last element of the list."""
        return self.client.rpop(self.name)

    def popleft(self):
        """Remove and return the first element of the list."""
        return self.client.lpop(self.name)

    def remove(self, value, count=1):
        """Remove occurences of ``value`` from the list.

        :keyword count: Number of matching values to remove.
            Default is to remove a single value.

        """
        count = self.client.lrem(self.name, value, num=count)
        if not count:
            raise ValueError("%s not in list" % value)
        return count

    def extend(self, iterable):
        """Append the values in ``iterable`` to this list."""
        for value in iterable:
            self.append(value)

    def extendleft(self, iterable):
        """Add the values in ``iterable`` to the head of this list."""
        for value in iterable:
            self.appendleft(value)


class Set(Type):
    """A set."""

    def __init__(self, name, client, initial=None):
        super(Set, self).__init__(name, client)
        if initial:
            self.update(initial)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_set())

    def __contains__(self, member):
        """``x.__contains__(member) <==> member in x``"""
        return self.client.sismember(self.name, member)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.scard(self.name)

    def _as_set(self):
        return self.client.smembers(self.name)

    def add(self, member):
        """Add element to set.

        This has no effect if the member is already present.

        """
        return self.client.sadd(self.name, member)

    def remove(self, member):
        """Remove element from set; it must be a member.

        :raises KeyError: if the element is not a member.

        """
        if not self.client.srem(self.name, member):
            raise KeyError(member)

    def pop(self):
        """Remove and return an arbitrary set element.

        :raises KeyError: if the set is empty.

        """
        member = self.client.spop(self.name)
        if member is not None:
            return member
        raise KeyError()

    def union(self, other):
        """Return the union of sets as a new set.

        (i.e. all elements that are in either set.)

        """
        return self.client.sunion([self.name, other.name])

    def update(self, other):
        """Update this set with the union of itself and others."""
        if isinstance(other, self.__class__):
            return self.client.sunionstore(self.name, [self.name, other.name])
        else:
            return map(self.add, other)

    def intersection(self, other):
        """Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)

        """
        return self.client.sinter([self.name, other.name])

    def intersection_update(self, other):
        """Update the set with the intersection of itself and another."""
        return self.client.sinterstore(self.name, [self.name, other.name])

    def difference(self, other):
        """Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)

        """
        return self.client.sdiff([self.name, other.name])

    def difference_update(self, other):
        """Remove all elements of another set from this set."""
        return self.client.sdiffstore(self.name, [self.name, other.name])


class SortedSet(Type):
    """A sorted set.

    :keyword initial: Initial data to populate the set with,
      must be an iterable of ``(element, score)`` tuples.

    """

    def __init__(self, name, client, initial=None):
        super(SortedSet, self).__init__(name, client)
        if initial:
            self.update(initial)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

    def __getslice__(self, start, stop):
        """``x.__getslice__(start, stop) <==> x[start:stop]``"""
        return self.client.zrange(self.name, start, stop - 1)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.zcard(self.name)

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_set())

    def add(self, member, score):
        """Add the specified member to the sorted set, or update the score
        if it already exist."""
        return self.client.zadd(self.name, member, score)

    def remove(self, member):
        """Remove member."""
        if not self.client.zrem(self.name, member):
            raise KeyError(member)

    def revrange(self, start=0, stop=-1):
        stop = stop is None and -1 or stop
        return self.client.zrevrange(self.name, start, stop)

    def increment(self, member, amount=1):
        """Increment the score of ``member`` by ``amount``."""
        return self.client.zincrby(self.name, member, amount)

    def rank(self, member):
        """Rank the set with scores being ordered from low to high."""
        return self.client.zrank(self.name, member)

    def revrank(self, member):
        """Rank the set with scores being ordered from high to low."""
        return self.client.zrevrank(self.name, member)

    def score(self, member):
        """Return the score associated with the specified member."""
        return self.client.zscore(self.name, member)

    def range_by_score(self, min, max):
        """Return all the elements with score >= min and score <= max
        (a range query) from the sorted set."""
        return self.client.zrangebyscore(self.name, min, max)

    def update(self, iterable):
        for member, score in iterable:
            self.add(member, score)

    def _as_set(self):
        return self.client.zrange(self.name, 0, -1)


class Dict(Type):
    """A dictionary."""

    def __init__(self, name, client, initial=None, **extra):
        super(Dict, self).__init__(name, client)
        initial = dict(initial or {}, **extra)
        if initial:
            self.update(initial)

    def __getitem__(self, key):
        """``x.__getitem__(key) <==> x[key]``"""
        value = self.client.hget(self.name, key)
        if value is not None:
            return value
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        """``x.__setitem__(key, value) <==> x[key] = value``"""
        return self.client.hset(self.name, key, value)

    def __delitem__(self, key):
        """``x.__delitem__(key) <==> del(x[key])``"""
        if not self.client.hdel(self.name, key):
            raise KeyError(key)

    def __contains__(self, key):
        """``x.__contains__(key) <==> key in x``"""
        return self.client.hexists(self.name, key)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.hlen(self.name)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return self.iteritems()

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_dict())

    def keys(self):
        """Returns the list of keys present in this dictionary."""
        return self.client.hkeys(self.name)

    def values(self):
        """Returns the list of values present in this dictionary."""
        return self.client.hvals(self.name)

    def items(self):
        """This dictionary as a list of ``(key, value)`` pairs, as
        2-tuples."""
        return self._as_dict().items()

    def iteritems(self):
        """Returns an iterator over the ``(key, value)`` items present in this
        dictionary."""
        return iter(self.items())

    def iterkeys(self):
        """Returns an iterator over the keys present in this dictionary."""
        return iter(self.keys())

    def itervalues(self):
        """Returns an iterator over the values present in this dictionary."""
        return iter(self.values())

    def has_key(self, key):
        """Returns ``True`` if ``key`` is present in this dictionary,
        ``False`` otherwise."""
        return key in self

    def get(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise returns
        ``default`` (``None`` by default.)"""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        """Returns the value at ``key`` if present, otherwise
        stores ``default`` value at ``key``."""
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def pop(self, key, default=None):
        """Remove specified key and return the corresponding value.

        If key is not found, ``default`` is returned if given,
        otherwise :exc:`KeyError` is raised.

        """
        try:
            val = self[key]
        except KeyError:
            val = default

        try:
            del(self[key])
        except KeyError:
            pass

        return val

    def update(self, other):
        """Update this dictionary with another."""
        return self.client.hmset(self.name, other)

    def _as_dict(self):
        return self.client.hgetall(self.name)


class Queue(Type):
    """FIFO Queue."""

    Empty = Empty
    Full = Full

    def __init__(self, name, client, initial=None, maxsize=0):
        super(Queue, self).__init__(name, client)
        self.list = List(name, client, initial)
        self.maxsize = maxsize
        self._pop = self.list.pop
        self._bpop = self.client.brpop
        self._append = self.list.appendleft

    def empty(self):
        """Return ``True`` if the queue is empty, or ``False``
        otherwise (not reliable!)."""
        return not len(self.list)

    def full(self):
        """Return ``True`` if the queue is full, ``False``
        otherwise (not reliable!).

        Only applicable if :attr:`maxsize` is set.

        """
        return self.maxsize and len(self.list) >= self.maxsize or False

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args ``block`` is ``True`` and ``timeout`` is
        ``None`` (the default), block if necessary until an item is
        available.  If ``timeout`` is a positive number, it blocks at
        most ``timeout`` seconds and raises the :exc:`Queue.Empty` exception
        if no item was available within that time. Otherwise (``block`` is
        ``False``), return an item if one is immediately available, else
        raise the :exc:`Queue.Empty` exception (``timeout`` is ignored
        in that case).

        """
        if not block:
            return self.get_nowait()
        item = self._bpop(self.name, timeout=timeout)
        if item is not None:
            return item
        raise Empty

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.

        :raises Queue.Empty: if an item is not immediately available.

        """
        item = self._pop()
        if item is not None:
            return item
        raise Empty()

    def put(self, item, **kwargs):
        """Put an item into the queue."""
        if self.full():
            raise Full()
        self._append(item)

    def qsize(self):
        """Returns the current size of the queue."""
        return len(self.list)


class LifoQueue(Queue):
    """Variant of :class:`Queue` that retrieves most recently added
    entries first."""

    def __init__(self, name, client, initial=None, maxsize=0):
        super(LifoQueue, self).__init__(name, client, initial, maxsize)
        self._pop = self.list.popleft
        self._bpop = self.client.blpop
