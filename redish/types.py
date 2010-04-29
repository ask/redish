from Queue import Empty, Full

from redish.utils import maybe_list, key
import bisect

class Type(object):

    def __init__(self, name, client):
        self.name = key(name)
        self.client = client


def Id(name, client):
    return "%s:%s" % (name, client.incr("ids:%s" % (name, )), )


class List(Type):
    """A list."""

    def __init__(self, name, client, initial=None):
        super(List, self).__init__(name, client)
        self.extend(initial or [])

    def extend(self, iterable):
        """Append the values in ``iterable`` to this list."""
        for value in iterable:
            self.append(value)

    def extendleft(self, iterable):
        """Add the values in ``iterable`` to the head of this list."""
        for value in iterable:
            self.appendleft(value)

    def __getitem__(self, index):
        """``x.__getitem__(index) <==> x[index]``"""
        return self.client.lindex(self.name, index)

    def __setitem__(self, index, value):
        """``x.__setitem__(index, value) <==> x[index] = value``"""
        return self.client.lset(self.name, index, value)

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
        return self.client.lrange(self.name, i, j)

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
        return self.client.ltrim(self.name, start, stop)

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


class Set(Type):
    """A set."""

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

    def union(self, others):
        """Return the union of sets as a new set.

        (i.e. all elements that are in either set.)

        """
        return self.client.sunion(other.name for other in maybe_list(others))

    def update(self, others):
        """Update this set with the union of itself and others."""
        return self.client.sunionstore(other.name
                                        for other in maybe_list(others))

    def intersection(self, others):
        """Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)

        """
        return self.client.sinter(other.name for other in maybe_list(others))

    def intersection_update(self, others):
        """Update the set with the intersection of itself and another."""
        return self.client.sinterstore(other.name
                                        for other in maybe_list(others))

    def difference(self, others):
        """Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)

        """
        return self.client.sdiff(other.name for other in maybe_list(others))

    def difference_update(self, others):
        """Remove all elements of another set from this set."""
        return self.client.sdiffstore(other.name
                                        for other in maybe_list(others))


class SortedSet(Type):
    """A sorted set."""

    def __getitem__(self, s):
        if isinstance(s, slice):
            i = s.start or 0
            j = s.stop or -1
        else:
            i = j = s
        return self.client.zrange(self.name, i, j)

    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return self.client.zcard(self.name)

    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())

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

    def increment(self, member, amount=1):
        """Increment the score of ``member`` by ``amount``."""
        return self.client.zincrby(self.name, member, amount)

    def rank(self, member):
        """Rank the set with scores being ordered from low to high."""
        return self.client.zrank(self.name, member)

    def reverse_rank(self, member):
        """Rank the set with scores being ordered from high to low."""
        return self.client.zrevrank(self.name, member)

    def score(self, member):
        """Return the score associated with the specified member."""
        return self.client.zscore(self.name, member)

    def range_by_score(self, min, max):
        """Return all the elements with score >= min and score <= max
        (a range query) from the sorted set."""
        return self.client.zrangebyscore(self.name, min, max)

    def _as_set(self):
        return self.client.zrange(self.name, 0, -1)
    
    def items(self):
        return self.client.zrange(self.name, 0, -1, withscores=True)



class Dict(Type):

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
        return iter(self.items())

    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_dict())

    def __cmp__(self, other):
        """``x.__cmp__(other) <==> cmp(x, other)``"""
        return cmp(self._as_dict(), other)

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
        return self.maxsize and len(self.list) > self.maxsize

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


class LIFOQueue(Queue):
    """LIFO Queue."""

    def __init__(self, name, client, initial=None, maxsize=0):
        super(LIFOQueue, self).__init__(name, client, initial, maxsize)
        self._pop = self.list.popleft
        self._bpop = self.client.blpop


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

class Int(Type):
    def __add__(self, other):
        return int.__add__(self.__int__(), other)
    
    def __sub__(self, other):
        return int.__sub__(self.__int__(), other)
    
    def __mul__(self, other):
        return int.__mul__(self.__int__(), other)
    
    def __div__(self, other):
        return int.__div__(self.__int__(), other)
    
    def __truediv__(self, other):
        return int.__truediv__(self.__int__(), other)
    
    def __floordiv__(self, other):
        return int.__floordiv__(self.__int__(), other)
    
    def __mod__(self, other):
        return int.__mod__(self.__int__(), other)
    
    def __divmod__(self, other):
        return int.__divmod__(self.__int__(), other)
    
    def __pow__(self, *args):
        return int.__pow__(self.__int__(), *args)
    
    def __lshift__(self, other):
        return int.__lshift__(self.__int__(), other)
    
    def __rshift__(self, other):
        return int.__rshift__(self.__int__(), other)
    
    def __and__(self, other):
        return int.__and__(self.__int__(), other)
    
    def __or__(self, other):
        return int.__or__(self.__int__(), other)
    
    def __xor__(self, other):
        return int.__xor__(self.__int__(), other)
    
    def __radd__(self, other):
        return int.__radd__(self.__int__(), other)
    
    def __rsub__(self, other):
        return int.__rsub__(self.__int__(), other)
    
    def __rmul__(self, other):
        return int.__rmul__(self.__int__(), other)
    
    def __rdiv__(self, other):
        return int.__rdiv__(self.__int__(), other)
    
    def __rtruediv__(self, other):
        return int.__rtruediv__(self.__int__(), other)
    
    def __rfloordiv__(self, other):
        return int.__rfloordiv__(self.__int__(), other)
    
    def __rmod__(self, other):
        return int.__rmod__(self.__int__(), other)
    
    def __rdivmod__(self, other):
        return int.__rdivmod__(self.__int__(), other)
    
    def __rpow__(self, *args):
        return int.__pow__(self.__int__(), *args)
    
    def __rlshift__(self, other):
        return int.__lshift__(self.__int__(), other)
    
    def __rrshift__(self, other):
        return int.__rshift__(self.__int__(), other)
    
    def __rand__(self, other):
        return int.__and__(self.__int__(), other)
    
    def __ror__(self, other):
        return int.__or__(self.__int__(), other)
    
    def __rxor__(self, other):
        return int.__xor__(self.__int__(), other)
    
    def __iadd__(self, other):
        self.client.incr(self.name, other)
        return self
    
    def __isub__(self, other):
        self.client.decr(self.name, other)
        return self
    
    def __imul__(self, other):
        self.client.set(self.name, int.__mul__(self.__int__(), other))
        return self
    
    def __idiv__(self, other):
        self.client.set(self.name, int.__div__(self.__int__(), other))
        return self
    
    def __itruediv__(self, other):
        self.client.set(self.name, int.__truediv__(self.__int__(), other))
        return self
    
    def __ifloordiv__(self, other):
        self.client.set(self.name, int.__floordiv__(self.__int__(), other))
        return self
    
    def __imod__(self, other):
        self.client.set(self.name, int.__mod__(self.__int__(), other))
        return self
    
    def __ipow__(self, other):
        self.client.set(self.name, int.__pow__(self.__int__(), other))
        return self
    
    def __iand__(self, other):
        self.client.set(self.name, int.__and__(self.__int__(), other))
        return self
    
    def __ior__(self, other):
        self.client.set(self.name, int.__or__(self.__int__(), other))
        return self
    
    def __ixor__(self, other):
        self.client.set(self.name, int.__xor__(self.__int__(), other))
        return self
    
    def __ilshift__(self, other):
        self.client.set(self.name, int.__lshift__(self.__int__(), other))
        return self
    
    def __irshift__(self, other):
        self.client.set(self.name, int.__rshift__(self.__int__(), other))
        return self
    
    def __neg__(self):
        return int.__neg__(self.__int__())
    
    def __pos__(self):
        return int.__pos__(self.__int__())
    
    def __abs__(self):
        return int.__abs__(self.__int__())
    
    def __invert__(self):
        return int.__invert__(self.__int__())
    
    def __long__(self):
        return int.__long__(self.__int__())
    
    def __float__(self):
        return int.__float__(self.__int__())
    
    def __complex__(self):
        return int.__complex__(self.__int__())
    
    def __int__(self):
        return int(self.client.get(self.name))
    
    def __repr__(self):
        return repr(int(self))
    

def is_zsettable(s):
    """quick check that all values in a dict are reals"""
    return all(map(lambda x: isinstance(x, (int, float, long)), s.values()))

class ZSet(object):
    """The simplest local implementation to Redis's Sorted Set imaginable.
    Little thought given to performance, simply get the basic implementation
    right."""
    def __init__(self, initial={}):
        if not is_zsettable(initial):
            raise ValueError(initial)
        self._dict = initial
    
    def items(self):
        return sorted(self._dict.items(), key=lambda x: (x[1], x[0]))
    
    def __getitem__(self, s):
        return self._as_set()[s]
    
    def __len__(self):
        """``x.__len__() <==> len(x)``"""
        return len(self._dict)
    
    def __iter__(self):
        """``x.__iter__() <==> iter(x)``"""
        return iter(self._as_set())
    
    def __repr__(self):
        """``x.__repr__() <==> repr(x)``"""
        return repr(self._as_set())
    
    def add(self, member, score):
        """Add the specified member to the sorted set, or update the score
        if it already exist."""
        self._dict[member] = score
    
    def remove(self, member):
        """Remove member."""
        del self._dict[member]
    
    def discard(self, member):
        if member in self._dict:
            del self._dict[member]
    
    def increment(self, member, amount=1):
        """Increment the score of ``member`` by ``amount``."""
        self._dict[member] += amount
        return self._dict[member]
    
    def rank(self, member):
        """Rank the set with scores being ordered from low to high."""
        return self._as_set().index(member)
    
    def reverse_rank(self, member):
        """Rank the set with scores being ordered from high to low."""
        return self.__len__() - self.rank(member) - 1
    
    def score(self, member):
        """Return the score associated with the specified member."""
        return self._dict[member]
    
    def range_by_score(self, min, max):
        """Return all the elements with score >= min and score <= max
        (a range query) from the sorted set."""
        data = self.items()
        keys = [r[1] for r in data] 
        start = bisect.bisect_left(keys, min)
        end = bisect.bisect_right(keys, max, start)
        return self._as_set()[start:end]
    
    def _as_set(self):
        return map(lambda x: x[0], self.items())
    
