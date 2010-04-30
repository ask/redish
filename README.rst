============================================================================
redish - Pythonic Redis abstraction built on top of redis-py
============================================================================

:Version: 0.0.1

Introduction
============


Examples
========


The client
----------

A connection to a database is represented by the ``redish.client.Client`` class::

    >>> from redish.client import Client
    >>> db = Client()
    >>> db = Client(host="localhost", port=6379, db="") # default settings.
    >>> db
    <RedisClient: localhost:6379/>

Serializers
-----------

Clients can be configured to automatically serialize and deserialize values.
There are three serializers shipped with ``redish``: ``Plain``, ``Pickler``
and ``JSON``::

    >>> from redish.serialization import Plain, Pickler, JSON

    >>> db = Client(serializer=Plain())
    >>> db = Client(serializer=Pickler())
    >>> db = Client(serializer=JSON())

In addition these serializers can also be configured to do
compression::

    # Using zlib compression
    >>> db = Client(serializer=Pickler(encoding="zlib"))


Working with keys and values
----------------------------

Set a value::

    >>> db["foo"] = {"name": "George"}

Get value by key::

    >>> db["foo"]
    {'name': 'George'}

Delete key::

    >>> del(db["foo"])

Getting nonexistent values works like you would expect from
Python dictionaries; It raises the KeyError exception::

    >>> db["foo"]
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "redish/client.py", line 198, in __getitem__
        raise KeyError(key)
    KeyError: 'foo'


Set many keys at the same time::

    >>> db.update({"name": "George Constanza",
    ...            "company": "Vandelay Industries"})

Get a list of keys in the database::

    >>> db.keys()
    ['company', 'name']

Get a list of keys matching a pattern::

    >>> db.keys(pattern="na*")
    ['name']

Rename keys::

    >>> db.rename("name", "user:name")
    >>> db.rename("company", "user:company")
    >>> db.keys("user:*")
    ['user:company', 'user:name']

Get all items in the database (optionally matching a pattern)
as a list of ``(key, value)`` tuples::

    >>> db.items(pattern="user:*")
    [('user:company', 'Vandelay Industries'), ('user:name', 'George Constanza')]

Get all values in the database (optionally where keys matches a pattern)::

    >>> db.values(pattern="user:*")
    ['Vandelay Industries', 'George Constanza']

Check for existence of a key in the database::

    >>> "user:name" in db
    True
    >>> "user:address" in db
    False
    >>> "user:address" not in db
    True

Get and remove key from the database (atomic operation)::

    >>> db.pop("user:name")
    'George Constanza'
    >>> "user:name" in db
    False

Get the number of keys present in the database::

    >>> len(db)
    1

Sets
----

Create a new set with the key ``myset``, and initial members
``"Jerry"`` and ``"George"``::

    >>> s = db.Set("myset", ["Jerry", "George"])

Add member ``"Elaine"`` to the set::

    >>> s.add("Elaine")

Check for membership::

    >>> "Jerry" in s
    True

    >>> "Cosmo" in s:
    False

Remove member from set::

    >>> s.remove("Elaine")
    >>> "Elaine" in s
    False

Get copy of the set as a ``list``::

    >>> list(s)
    ['Jerry', 'George']

Create another set::

    >>> s2 = x.Set("myset2", ["Jerry", "Jason", "Julia", "Michael")

Get the difference of the second set and the first::

    >>> s2.difference(s)
    set(['Jason', 'Michael', 'Julia'])

Get the union of the two sets::

    >>> s.union(s2)
    set(['Jason', 'Michael', 'Jerry', 'Julia', 'George'])

Get the intersection of the two sets::

    >>> s.intersection(s2)
    set(['Jerry'])

Update the set with the union of another::

    >>> s.update(s2)
    5
    >>> s
    <Set: ['Jason', 'Michael', 'Jerry', 'Julia', 'George']>

Sorted sets
-----------

Create a new sorted set with the key ``myzset``, and initial members::

    >>> z = db.SortedSet("myzset", (("foo", 0.9), ("bar", 0.1), ("baz", 0.3)))

Casting to list gives the members ordered by score::

    >>> list(z)
    ['bar', 'baz', 'foo']

``revrange`` sorts the members in reverse::

    >>> z.revrange()
    ['foo', 'baz', 'bar']

``score`` gives the current score of a member::

    >>> z.score("foo")
    0.90000000000000002

``add`` adds another member::

    >>> z.add("zaz", 1.2)
    >>> list(z)
    ['bar', 'baz', 'foo', 'zaz']

``increment`` increments the score of a member by ``amount`` (or 1 by
default)::

    >>> z.increment("baz")
    1.3
    >>> z.increment("bar", 0.2)
    0.30000000000000004
    >>> list(z)
    ['bar', 'foo', 'zaz', 'baz']

Check for membership using the ``in`` operator::

    >>> "bar" in z
    True

    >>> "xuzzy" in z
    False

``remove`` removes a member::

    >>> z.remove("zaz")
    >>> "zaz" in z
    False

``update`` updates the sorted set with members from an iterable of ``(member,
score)`` tuples::

    >>> z.update([("foo", 0.1), ("xuzzy", 0.6)])
    >>> list(z)
    ['foo', 'bar', 'xuzzy', 'baz']

``rank`` gives the position of a member in the set (0-based)::

    >>> z.rank("foo")
    0
    >>> z.rank("xuzzy")
    2

``revrank`` gives the position of a member in reverse order::

    >>> z.revrank("foo")
    3
    >>> z.revrank("baz")
    0

``range_by_score`` gives all the member with score within a range (``min`` /
``max``)::

    >>> z.range_by_score(min=0.3, max=0.6)
    ['bar', 'xuzzy']


Installation
============

You can install ``redish`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install redish


To install using ``easy_install``,::

    $ easy_install redish


If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root

Examples
========

.. Please write some examples using your package here.
