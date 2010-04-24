import operator


def maybe_list(value):
    # FIXME
    if not operator.isSequenceType(value):
        return [value]
    return value


class Type(object):

    def __init__(self, name, client):
        self.name = name
        self.client = client


class List(Type):

    def __getitem__(self, index):
        return self.client.lindex(self.name, index)

    def __setitem__(self, index, value):
        return self.client.lset(self.name, index, value)

    def __len__(self):
        return self.client.llen(self.name)

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

    def __iter__(self):
        return iter(self.client.smembers(self.name))

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

    def add(self, member, score):
        return self.client.zadd(self.name, member, score)

    def remove(self, member):
        if not self.client.zrem(self.name, member):
            raise KeyError(member)
