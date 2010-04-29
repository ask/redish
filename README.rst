============================================================================
redish - Pythonic Redis abstraction built on top of redis-py
============================================================================

:Version: 0.0.1.1

Introduction
============

By mixing Åsk's type system from redish with the original redis-py's Redis
object, this fork gives a different sort of transparent access to the
key-value store without pickling/unpickling and by respecting the strengths
in Redis's types.

Braindump::

    >>> from redish.proxy import Proxy
    >>> x = Proxy()

    # Key/Value with strings
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
    
    # Int/Counter
    >>> x["z"] = 1
    >>> x["z"]
    1
    >>> x["z"].__class__
    <class 'redish.types.Int'>
    >>> x["z"] += 2
    >>> x["z"]
    3
    >>> 3 * x["z"]
    9
    >>> z = x["z"]
    >>> z += 1
    >>> z
    4
    >>> x["z"]
    4
    # Don't get tripped up on assignment:
    >>> z = 5
    >>> x["z"]
    4
    >>> z
    5
    >>> z.__class__
    <type 'int'>
    

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
    
    # List
    >>> x["Liszt"] = ['w', 'x', 'y', 'z']
    >>> x["Liszt"]
    ['w', 'x', 'y', 'z']
    >>> x["Liszt"].extend(["a", "b", "c"])
    >>> x["Liszt"]
    ['w', 'x', 'y', 'z', 'a', 'b', 'c']
    >>> x["Liszt"][-1]
    'c'
    >>> x["Liszt"].pop()
    'c'
    >>> x["Liszt"][-1]
    'b'
    
    # Set
    >>> x["set"] = set(["opera", "firefox", "ie", "safari"])
    >>> s = x["set"]
    >>> "opera" in s
    True
    >>> s.remove("safari")
    >>> "safari" in s
    False
    >>> list(s)
    ['opera', 'ie', 'firefox']
    
    # N.B. Assignment copies by value.
    >>> x["game"] = x["set"]
    >>> x["game"].add("mobilesafari")
    True
    >>> x["game"]
    set(['opera', 'ie', 'firefox', 'mobilesafari'])
    >>> x["set"]
    set(['opera', 'ie', 'firefox'])
    
    # Sorted Set (Local and Remote)
    >>> from redish.types import ZSet
    >>> zs = ZSet({'c': 3, 'b': 2, 'a': 1})
    >>> zs
    ['a', 'b', 'c']
    >>> zs[-1]
    'c'
    >>> x["zs"] = zs
    >>> x["zs"].rank("a")
    0
    >>> x["zs"].range_by_score(2,3)
    ['b', 'c']
    >>> x["zs"].remove("c")
    >>> x["zs"].items()
    [('a', 1.0), ('b', 2.0)]
    
    # Proxy object retains all the normal methods from Redis object
    >>> x.keys()
    ['z', 'dictionary', 'Liszt', 'set', 'game']
    >>> x.bgsave()
    True
    
        
Installation
============

If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root

Examples
========

.. Please write some examples using your package here.
