import unittest2 as unittest
from datetime import datetime

from redish import utils


class test_maybe_list(unittest.TestCase):

    def test_list(self):
        self.assertListEqual(utils.maybe_list([1, 2, 3]), [1, 2, 3])

    def test_value(self):
        self.assertListEqual(utils.maybe_list(1), [1])

    def test_None(self):
        self.assertListEqual(utils.maybe_list(None), [])


class test_utils(unittest.TestCase):

    def test_mkey(self):
        self.assertEqual(utils.mkey("foo"), "foo")
        self.assertEqual(utils.mkey("foo:bar"), "foo:bar")
        self.assertEqual(utils.mkey(("foo", "bar", "baz")), "foo:bar:baz")
        self.assertEqual(utils.mkey(["foo", "bar", "baz"]), "foo:bar:baz")

    def test_dt_to_timestamp(self):
        dt = datetime(2010, 4, 29, 13, 49, 34, 112487)
        self.assertEqual(utils.dt_to_timestamp(dt), 1272541774.0)

    def test_maybe_datetime(self):
        self.assertEqual(utils.maybe_datetime(
                            datetime(2010, 4, 29, 13, 49, 34, 112487)),
                         1272541774.0)
        self.assertEqual(utils.maybe_datetime(1272541774.0), 1272541774.0)
