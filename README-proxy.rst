============================================================================
redish - Pythonic Redis abstraction built on top of redis-py
============================================================================

Proxy
=====

By mixing the type system from redish with the original redis-py's Redis
object, the redish.proxy module gives a different sort of transparent access
to the key-value store without pickling/unpickling and by respecting the
strengths in Redis's types. In other words, it respects Redis as a data
structure server.

Basics
------

Example::

    >>> from redish import proxy
    >>> x = proxy.Proxy()

Ordinary key/value usage encodes strings as UTF-8, and returns unicode 
objects when accessing by key::

    >>> x["foo"] = "bar"
    >>> x["foo"]
    u'bar'

Deletion and invalid keys work as expected::

    >>> del(x["foo"])
    >>> x["foo"]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "redish/proxy.py", line 29, in __getitem__
        raise KeyError(key)
    KeyError: 'foo'
    
Integer (or Counter)
--------------------

When reading an integer, the proxy transparently passes an object that mimics
the behaviour of int, but is actually stored and fetched from the Redis store::

    >>> x["z"] = 1
    >>> x["z"]
    1
    >>> x["z"].__class__
    <class 'redish.types.Int'>
    
Increment and decrement operations translate directly to Redis commands::

    >>> x["z"] += 2
    >>> x["z"]
    3

And all other operations you would expect to perform on an integer are present::

    >>> 3. * x["z"]
    9.0

The proxy object can be assigned to another variable, and it will point to the
same value in the Redis store. For the most part, you can treat the variable
the same way::

    >>> z = x["z"]
    >>> z += 1
    >>> z
    4
    >>> x["z"]
    4

However, it is not the same in all respects: reassigning the variable is not
the same as setting the value on the key::

    >>> z = 5
    >>> x["z"]
    4
    >>> z
    5
    >>> z.__class__
    <type 'int'>
    
Dictionary
----------

By assigning a key to a dictionary type, a hash data type is created in the
Redis store. When the key is accessed, it returns a type that mimics a python
dict::

    >>> x["dictionary"] = {"a": "b", "c": "d"} 
    >>> x["dictionary"] 
    {'a': 'b', 'c': 'd'}

You may access, create, test, and destroy keys within that hash as if they
were native Python keys in a dict::

    >>> x["dictionary"]["c"]
    'd'
    >>> x["dictionary"]["e"] = "f"
    >>> "e" in x["dictionary"]
    True
    >>> x["dictionary"].__class__
    <class 'redish.types.Dict'>
    
List
----

By assigning a key in the Proxy object to a list type, a list is created in
the Redis store. When the key is accessed, it returns a type that mimics a
python list::

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
    
Set
---

By assigning a key in the Proxy object to a set type, a set is created in the
Redis store. When the key is accessed, it returns a type that mimics a python
set::

    >>> x["set"] = set(["opera", "firefox", "ie", "safari"])
    >>> s = x["set"]
    >>> "opera" in s
    True
    >>> s.remove("safari")
    >>> "safari" in s
    False
    >>> list(s)
    ['opera', 'ie', 'firefox']

It may be useful to point out that assignment to a key on the proxy object
copies by value::

    >>> x["game"] = x["set"]
    >>> x["game"].add("mobilesafari")
    True
    >>> x["game"]
    set(['opera', 'ie', 'firefox', 'mobilesafari'])
    >>> x["set"]
    set(['opera', 'ie', 'firefox'])

Sorted Set
----------

There is no native Python equivalent of a Sorted Set. However, it resembles a
specialized dictionary in which all the values are numeric. The local
implementation of the Sorted Set type (ZSet) uses a dictionary in this way to
initialize its values::

    >>> from redish.types import ZSet
    >>> zs = ZSet({'c': 3, 'b': 2, 'a': 1})
    >>> zs
    ['a', 'b', 'c']
    >>> zs[-1]
    'c'

The proxied equivalent in which the data resides on the Redis server is
created when setting a key to an object of the ZSet class, and is generated
when retrieving such a set::

    >>> x["zs"] = zs
    >>> x["zs"].rank("a")
    0
    >>> x["zs"].range_by_score(2,3)
    ['b', 'c']
    >>> x["zs"].remove("c")
    >>> x["zs"].items()
    [('a', 1.0), ('b', 2.0)]

Proxy objects in general
------------------------
A Proxy object retains all the normal methods from Redis object::

    >>> x.keys()
    ['z', 'dictionary', 'Liszt', 'set', 'game']
    >>> x.bgsave()
    True
