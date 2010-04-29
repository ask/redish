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


