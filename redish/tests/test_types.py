from __future__ import with_statement

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
        self.assertListEqual(l[0:2], ["foo", "bar"])

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
