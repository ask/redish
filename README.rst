============================================================================
redish - Pythonic Redis abstraction built on top of redis-py
============================================================================

:Version: 0.0.1

Introduction
============

Braindump::

    >>> from redish.client import Client
    >>> x = Client()

    # Key/Value
    >>> x["foo"] = {"name": "George"}
    >>> x["foo"]
    {'name': 'George'}
    >>> del(x["foo"])
    >>> x["foo"]
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "redish/client.py", line 52, in __getitem__
        raise KeyError(key)
    KeyError: 'foo'

    # Sets

    >>> s = x.Set("myset")
    >>> map(s.add, ["opera", "firefox", "ie", "safari"])
    [True, True, True, True]
    >>> "opera" in s
    True
    >>> s.remove("safari")
    >>> "safari" in s
    False
    >>> list(s)
    ['opera', 'ie', 'firefox']
    >>> s2 = x.Set("myset2")
    >>> map(s2.add, ["opera", "firefox", "mosaic"])
    [True, True, True]
    >>> s.difference(s2)
    set(['opera', 'firefox', 'mosaic'])

    # Sorted Set

    >>> z = x.SortedSet("myzset")
    >>> z.add("foo", 0.9)  
    True
    >>> z.add("bar", 0.1)
    True
    >>> z.add("baz", 0.3)
    True
    >>> z[0:3]
    ['bar', 'baz', 'foo']



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
