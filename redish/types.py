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
