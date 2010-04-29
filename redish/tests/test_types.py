from __future__ import with_statement

from redish import types
from redish.client import ResponseError
from redish.tests.test_client import ClientTestCase


class test_List(ClientTestCase):

    def test_get_set_item(self):
        names = ("George Constanza", "Jerry Seinfeld",
                 "Kosmo Kramer", "Elaine Marie Benes")
        l = self.client.List("test:List:get_set_item", names)
        for i, name in enumerate(names):
            self.assertEqual(l[i], name)

        with self.assertRaises(IndexError):
            l[99]

        revnames = list(reversed(names))
        for i, name in enumerate(revnames):
            l[i] = name
        for i, name in enumerate(revnames):
            self.assertEqual(l[i], name)

        with self.assertRaises(IndexError):
            l[99] = "value"

    def test__setitem__respects_custom_error(self):

        class MockClient(object):

            def lset(self, *args, **kwargs):
                raise ResponseError("connection lost")

        l = self.client.List("test:List:__setitem__ResponseError")
        l.client = MockClient()

        with self.assertRaises(ResponseError):
            l[1] = 2

    def test__len__(self):
        initial = range(100)
        l = self.client.List("test:List:__len__", initial)
        self.assertEqual(len(l), len(initial))
        l2 = self.client.List("test:List:__len__:empty")
        self.assertEqual(len(l2), 0)

    def test__repr__(self):
        l = self.client.List("test:List:__repr__", [1, 2, 3])
        self.assertIn("'1', '2', '3'", repr(l))

    def test__iter__(self):
        data = ["foo", "bar", "baz"]
        l = self.client.List("test:List:__iter__", data)
        self.assertListEqual(list(iter(l)), data)

    def test__getslice__(self):
        data = ["foo", "bar", "baz", "xuzzy"]
        l = self.client.List("test:List:__getslice__", data)
        self.assertListEqual(l[:2], ["foo", "bar"])
        self.assertListEqual(l[:-1], ["foo", "bar", "baz"])

    def test_append(self):
        data = ["foo", "bar", "baz"]
        l = self.client.List("test:List:append", data)
        l.append("xuzzy")
        self.assertListEqual(list(l), data + ["xuzzy"])

    def test_appendleft(self):
        data = ["foo", "bar", "baz"]
        l = self.client.List("test:List:append", data)
        l.appendleft("xuzzy")
        self.assertListEqual(list(l), ["xuzzy"] + data)

    def test_trim(self):
        data = map(str, range(100))
        l = self.client.List("test:List:trim", data)
        l.trim(0, 50)
        self.assertListEqual(list(l), data[:50])

    def test_pop(self):
        data = ["foo", "bar", "baz"]
        l = self.client.List("test:List:pop", data)
        self.assertEqual(l.pop(), "baz")

    def test_popleft(self):
        data = ["foo", "bar", "baz"]
        l = self.client.List("test:List:popleft", data)
        self.assertEqual(l.popleft(), "foo")

    def test_remove(self):
        data = ["foo", "bar", "baz", "bar", "baz", "bar", "bar", "bar"]
        l = self.client.List("test:List:remove", data)
        l.remove("bar")
        self.assertEqual(len(l), len(data) - 1)
        l.remove("bar", 100)
        self.assertEqual(len(l), 3)

        with self.assertRaises(ValueError):
            l.remove("nonexistent")

    def test_extend(self):
        data1 = ["foo", "bar", "baz"]
        data2 = ["Bart", "Lisa", "Homer", "Marge", "Maggie"]
        l = self.client.List("test:List:extend", data1)
        l.extend(data2)
        self.assertListEqual(list(l), data1 + data2)

    def test_extendleft(self):
        data1 = ["foo", "bar", "baz"]
        data2 = ["Bart", "Lisa", "Homer", "Marge", "Maggie"]
        l = self.client.List("test:List:extend", data1)
        l.extendleft(data2)
        self.assertListEqual(list(l), list(reversed(data2)) + data1)


class test_Set(ClientTestCase):

    def test_no_initial_data(self):
        s = self.client.Set("test:Set:no_initial_data")
        self.assertEqual(len(s), 0)

    def test__iter__(self):
        data = ["foo", "bar", "baz", "zaz"]
        s = self.client.Set("test:Set:__iter__", data)
        self.assertItemsEqual(list(iter(s)), list(set(data)))

    def test__repr__(self):
        data = ["foo", "bar", "baz"]
        s = self.client.Set("test:Set:__repr__", data)
        self.assertIn("'foo'", repr(s))

    def test__contains__(self):
        data = ["foo", "bar", "baz"]
        s = self.client.Set("test:Set:__contains__", data)
        self.assertIn("foo", s)
        self.assertNotIn("zaz", s)

    def test__len__(self):
        data = range(100)
        s = self.client.Set("test:Set:__len__", data)
        self.assertEqual(len(s), 100)

    def test_add(self):
        data = ["foo", "bar", "baz"]
        s = self.client.Set("test:Set:add", data)
        s.add("zaz")
        self.assertIn("zaz", s)

    def test_remove(self):
        data = ["foo", "bar", "baz", "zaz"]
        s = self.client.Set("test:Set:remove", data)
        s.remove("foo")
        self.assertNotIn("foo", s)
        with self.assertRaises(KeyError):
            s.remove("xuzzy")

    def test_pop(self):
        data = set(["foo", "bar", "baz", "zaz"])
        s = self.client.Set("test:Set:remove", data)
        member = s.pop()
        self.assertIn(member, data)
        self.assertNotIn(member, s)
        self.assertEqual(len(s), len(data) - 1)

    def test_pop_empty_set_raises_KeyError(self):
        s = self.client.Set("test:Set:pop_empty_set")
        with self.assertRaises(KeyError):
            s.pop()

    def test_union(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:union:1", ds1)
        s2 = self.client.Set("test:Set:union:2", ds2)
        u = s1.union(s2)
        self.assertSetEqual(ds1.union(ds2), u)

    def test_update_redis_set(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:update_redis_set:1", ds1)
        s2 = self.client.Set("test:Set:update_redis_set:2", ds2)
        s1.update(s2)
        self.assertSetEqual(s1._as_set(), ds1.union(ds2))

    def test_update_pyset(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:update_pyset", ds1)
        s1.update(ds2)
        self.assertSetEqual(s1._as_set(), ds1.union(ds2))

    def test_intersection(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:intersection:1", ds1)
        s2 = self.client.Set("test:Set:intersection:2", ds2)
        self.assertSetEqual(s1.intersection(s2), ds1.intersection(ds2))

    def test_intersection_update(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:intersection_update:1", ds1)
        s2 = self.client.Set("test:Set:intersection_update:2", ds2)
        s1.intersection_update(s2)
        self.assertSetEqual(s1._as_set(), ds1.intersection(ds2))

    def test_difference(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:difference:1", ds1)
        s2 = self.client.Set("test:Set:difference:2", ds2)
        self.assertSetEqual(s1.difference(s2), ds1.difference(ds2))

    def test_difference_update(self):
        ds1 = set(["foo", "bar", "baz"])
        ds2 = set(["baz", "xuzzy", "zaz"])
        s1 = self.client.Set("test:Set:difference_update:1", ds1)
        s2 = self.client.Set("test:Set:difference_update:2", ds2)
        s1.difference_update(s2)
        self.assertSetEqual(s1._as_set(), ds1.difference(ds2))


class test_SortedSet(ClientTestCase):

    def test_no_initial_data(self):
        z = self.client.SortedSet("test:SortedSet:no_initial_data")
        self.assertEqual(len(z), 0)

    def test__iter__(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:__iter__", data)
        self.assertListEqual(list(iter(z)), ["bar", "baz", "foo"])

    def test__getslice__(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:__getslice__", data)
        self.assertListEqual(z[0:2], ["bar", "baz"])
        self.assertListEqual(z[0:-1], ["bar", "baz"])

    def test__len__(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:__len__", data)
        self.assertEqual(len(z), len(data))

    def test__repr__(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:__repr__", data)
        self.assertIn("'foo'", repr(z))

    def test_add(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:add", data)
        z.add("xuzzy", 0.4)
        self.assertListEqual(list(z), ["bar", "baz", "xuzzy", "foo"])

    def test_remove(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:remove", data)
        z.remove("bar")
        self.assertListEqual(list(z), ["baz", "foo"])

        with self.assertRaises(KeyError):
            z.remove("nonexistent")

    def test_revrange(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:revrange", data)
        self.assertListEqual(z.revrange(), ["foo", "baz", "bar"])

    def test_increment(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:increment", data)
        z.increment("bar", 1)
        self.assertListEqual(list(z), ["baz", "foo", "bar"])

    def test_rank(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:rank", data)
        self.assertEqual(z.rank("bar"), 0)
        self.assertEqual(z.rank("baz"), 1)
        self.assertEqual(z.rank("foo"), 2)

    def test_revrank(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:revrank", data)
        self.assertEqual(z.revrank("bar"), 2)
        self.assertEqual(z.revrank("baz"), 1)
        self.assertEqual(z.revrank("foo"), 0)

    def test_score(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        z = self.client.SortedSet("test:SortedSet:score", data)
        for member, score in data:
            self.assertEqual(z.score(member), score)

    def test_update(self):
        data1 = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3))
        data2 = (("bar", 1.2), ("xuzzy", 0.2), ("zaz", 0.4))
        z = self.client.SortedSet("test:SortedSet:update", data1)
        z.update(data2)
        self.assertListEqual(list(z), ["xuzzy", "baz", "zaz", "foo", "bar"])

    def test_range_by_score(self):
        data = (("foo", 0.9), ("bar", 0.1), ("baz", 0.3),
                 ("bam", 1.2), ("xuzzy", 0.2), ("zaz", 0.4))
        z = self.client.SortedSet("test:SortedSet:range_by_score", data)
        self.assertListEqual(z.range_by_score(0.3, 1.0), [
                                "baz", "zaz", "foo"])


class test_Dict(ClientTestCase):

    def test__init__(self):
        data = {"name": "George Constanza"}
        d = self.client.Dict("test:Dict:__init__", data,
                             company="Vandelay Industries")
        self.assertEqual(d["name"], "George Constanza")
        self.assertEqual(d["company"], "Vandelay Industries")

    def test__missing__(self):

        class MissingDict(types.Dict):

            def __missing__(self, key):
                return 42

        d = MissingDict("test:Dict:__missing__", self.client.api)
        self.assertEqual(d["nonexistent"], 42)

    def test_set_get_delete(self):
        d = self.client.Dict("test:Dict:set_get_delete")
        d["foo"] = "bar"
        self.assertEqual(d["foo"], "bar")
        del(d["foo"])
        with self.assertRaises(KeyError):
            d["foo"]
        with self.assertRaises(KeyError):
            del(d["foo"])

    def test__getitem__raises_KeyError(self):
        d = self.client.Dict("test:Dict:__getitem__raises_KeyError")
        with self.assertRaises(KeyError):
            d["nonexistent"]

    def test__contains__(self):
        d = self.client.Dict("test:Dict:__contains__", {"name": "Jerry"})
        self.assertIn("name", d)
        self.assertNotIn("address", d)

    def test__len__(self):
        d = self.client.Dict("test:Dict:__len__", dict((i, i)
                                                    for i in range(100)))
        self.assertEqual(len(d), 100)

    def test__iter__(self):
        # also tests d.iteritems() + d.items()
        items = dict((i, i) for i in map(str, range(100)))
        d = self.client.Dict("test:Dict:__iter__", items)
        self.assertListEqual(list(iter(d)), items.items())

    def test__repr__(self):
        d = self.client.Dict("test:Dict:__repr__", foo="bar")
        self.assertIn("'foo': 'bar'", repr(d))

    def test_iterkeys(self):
        # also tests d.keys()
        items = dict((i, i) for i in map(str, range(100)))
        d = self.client.Dict("test:Dict:iterkeys", items)
        self.assertItemsEqual(list(d.iterkeys()), items.keys())

    def test_itervalues(self):
        # also tests d.values()
        items = dict((i, i) for i in map(str, range(100)))
        d = self.client.Dict("test:Dict:itervalues", items)
        self.assertItemsEqual(list(d.itervalues()), items.values())

    def test_has_key(self):
        d = self.client.Dict("test:Dict:has_key", foo="bar")
        self.assertTrue(d.has_key("foo"))
        self.assertFalse(d.has_key("bar"))

    def test_get(self):
        d = self.client.Dict("test:Dict:get", foo="bar")
        self.assertEqual(d.get("foo"), "bar")
        self.assertIsNone(d.get("bar"))
        self.assertEqual(d.get("bar", 12345), 12345)

    def test_setdefault(self):
        d = self.client.Dict("test:Dict:setdefault")
        self.assertEqual(d.setdefault("somekey", "54321"), "54321")
        self.assertEqual(d["somekey"], "54321")

        d["otherkey"] = "56789"
        self.assertEqual(d.setdefault("otherkey", "12345"), "56789")
        self.assertEqual(d["otherkey"], "56789")

    def test_pop(self):
        d = self.client.Dict("test:Dict:pop", foo="bar")
        self.assertIsNone(d.pop("nonexistent"))
        self.assertEqual(d.pop("nonexistent", "12345"), "12345")
        self.assertEqual(d.pop("foo"), "bar")
        self.assertIsNone(d.pop("foo"))

        with self.assertRaises(KeyError):
            d["foo"]

    def test_update(self):
        data1 = {"George Constanza": "architect",
                 "Jerry Seinfeld": "comedian"}
        data2 = {"Elaine Marie Benes": "assistant"}
        d = self.client.Dict("test:Dict:update", data2)
        d.update(data1)
        self.assertDictContainsSubset(data1, dict(d))



class QueueCase(ClientTestCase):

    def setUp(self):
        super(QueueCase, self).setUp()
        self.setUpQueue()

    def setUpQueue(self):
        self.qtype = None

    def test_empty(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:empty")
        self.assertTrue(q.empty())
        q.put("foo")
        self.assertFalse(q.empty())

    def test_full(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:full:1", maxsize=None)
        self.assertFalse(q.full())

        q2 = self.qtype("test:Queue:full:2", maxsize=10)
        [q2.put(i) for i in map(str, range(10))]
        self.assertTrue(q2.full())

    def test_put_get(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:put_get")
        q.put("foo")
        self.assertEqual(q.get(block=False), "foo")

    def test_get_raises_Empty(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:get_raises_Empty")
        with self.assertRaises(q.Empty):
            q.get(block=False)

    def test_put_raises_Full(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:put_raises_Full", maxsize=3)
        q.put("foo")
        q.put("bar")
        q.put("baz")
        self.assertTrue(q.full())
        with self.assertRaises(q.Full):
            q.put("xuzzy")

    def test_qsize(self):
        if not self.qtype:
            return
        q = self.qtype("test:Queue:qsize")
        self.assertEqual(q.qsize(), 0)
        [q.put(i) for i in range(100)]
        self.assertEqual(q.qsize(), 100)


class test_Queue(QueueCase):

    def setUpQueue(self):
        self.qtype = self.client.Queue

    def test_is_FIFO(self):
        items = ("foo", "bar", "baz")
        q = self.qtype("test:Queue:is_FIFO")
        for item in items:
            q.put(item)
        for item in items:
            self.assertEqual(q.get(block=False), item)


class test_LifoQueue(QueueCase):

    def setUpQueue(self):
        self.qtype = self.client.LifoQueue

    def test_is_LIFO(self):
        items = ("foo", "bar", "baz")
        q = self.qtype("test:Queue:is_LIFO")
        for item in items:
            q.put(item)
        for item in reversed(items):
            self.assertEqual(q.get(block=False), item)
