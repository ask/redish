============================================================================
redish - Pythonic Redis abstraction built on top of redis-py
============================================================================

:Version: 0.0.1.1

Introduction
============

By mixing the original redish's type system with the original redis-py's Redis
object, give a different sort of transparent access to the key-value store
without pickling/unpickling.

Braindump::

    >>> from redish.proxy import Proxy
    >>> x = Proxy()

    # Key/Value
    >>> x["foo"] = "bar"
    >>> x["foo"]
    'bar'
    >>> del(x["foo"])
    >>> x["foo"]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "redish/proxy.py", line 29, in __getitem__
        raise KeyError(key)
    KeyError: 'foo'

    # Dict
    
    >>> x["dictionary"] = {"a": "b", "c": "d"}
    >>> x["dictionary"]
    {'a': 'b', 'c': 'd'}
    >>> x["dictionary"]["c"]
    'd'
    >>> x["dictionary"]["e"] = "f"
    >>> "e" in x["dictionary"]
    True
    >>> x["dictionary"].__class__
    <class 'redish.types.Dict'>
    
    # Sets

    >>> x["set"] = set(["opera", "firefox", "ie", "safari"])
    >>> s = x["set"]
    >>> "opera" in s
    True
    >>> s.remove("safari")
    >>> "safari" in s
    False
    >>> list(s)
    ['opera', 'ie', 'firefox']


Installation
============

If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root

Examples
========

.. Please write some examples using your package here.
