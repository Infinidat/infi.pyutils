Overview
========

.. image:: https://travis-ci.org/Infinidat/infi.pyutils.png?branch=master

*infi.pyutils* is a set of utilities for various tasks in Python.

Contents
========

Iteration Utilities
---------------

iterate
+++++++

*iterate* is a django-style for loop over elements, yielding convenient information about the iterated collection::

 >>> from __future__ import print_function
 >>> from infi.pyutils import iterate
 >>> for iteration, element in iterate(range(3)):
 ...     print(element)
 ...     print(iteration.first)
 ...     print(iteration.counter0)
 ...     print(iteration.counter1)
 ...     print(iteration.last)
 0
 True
 0
 1
 False
 1
 False
 1
 2
 False
 2
 False
 2
 3
 True

This even works for generators and other iterables::

 >>> list(iterate(i for i in range(3)))[-1][0].last
 True

 .. note:: For iterated collections which are not simple ones (i.e. generators or other types), some prefetching is made to determing last elements

renumerate
++++++++++

*renumerate* is like *enumerate*, only backwards. This is useful for popping from a list in-place::

  >>> from infi.pyutils import renumerate
  >>> l = [1, 2, 3, 4]
  >>> for index, element in renumerate(l):
  ...     if element % 2 == 0:
  ...         unused = l.pop(index)
  >>> l
  [1, 3]

This also works for generators (although slightly less efficient):

  >>> x = list(renumerate(i for i in range(3)))
  >>> x
  [(2, 2), (1, 1), (0, 0)]

*infi.pyutils* provides a set of mixin classes to make objects comparable and hashable based on a single key::

  >>> from infi.pyutils import ComparableByKey
  >>> class MyComparableType(ComparableByKey):
  ...     def __init__(self, value):
  ...         super(MyComparableType, self).__init__()
  ...         self.value = value
  ...     def _get_key(self):
  ...         return self.value
  >>> MyComparableType("c") > MyComparableType("b")
  True

Reflection
----------

Method Map
++++++++++

Method maps is intended for the repeating pattern described below:
::

  >>> class Handler(object):
  ...     def handle_string(self, s):
  ...         if s == 'some.string.1':
  ...             return self._handle_string_1()
  ...         elif s == 'some.string.2':
  ...             return self._handle_string_2()
  ...         raise NotImplementedError()

If the strings can be legitimate python variable names, one would interpolate the string in the handler name, and then use getattr to get them. Unfortunately, this is not possible with any string (and also not very explicit).

Using Method Maps is pretty straightforward:

  >>> from infi.pyutils.method_map import MethodMap
  >>> class Handler(object):
  ...     HANDLERS = MethodMap()
  ...     @HANDLERS.registering('some.string.1')
  ...     def _handle_string_1(self):
  ...         return 1
  ...     @HANDLERS.registering('some.string.2')
  ...     def _handle_string_2(self):
  ...         return 2
  ...     def handle_string(self, s):
  ...         handler = self.HANDLERS.get(s, None)
  ...         if handler is None:
  ...             raise NotImplementedError()
  ...         return handler()
  >>> h = Handler()
  >>> h.handle_string('some.string.1')
  1
  >>> h.handle_string('some.string.2')
  2
  >>> h.handle_string('bla') # doctest: +IGNORE_EXCEPTION_DETAIL
  Traceback (most recent call last):
    ...
  NotImplementedError

Functors
--------
*infi.pyutils.functors* is a utility package for working with function or function-like objects.

Misc. Functors
++++++++++++++
*Always* is used to constantly return a value:
::

  >>> from infi.pyutils.functors import Always
  >>> a = Always(5)
  >>> a
  <Always 5>
  >>> a()
  5
  >>> a(1, 2, 3)
  5

*Identity* is a functor that always returns its single argument:
::

  >>> from infi.pyutils.functors import Identity
  >>> Identity
  <Identity>
  >>> Identity(2)
  2
  >>> obj = object()
  >>> Identity(obj) is obj
  True

PASS
++++

PASS is a 'null functor'. You can always call it anyway you like, it will always return None::

  >>> from infi.pyutils.functors import PASS
  >>> PASS(1, 2, 3)
  >>> PASS(666, a=2, c=4)

You can also use it as a context manager that does nothing::

  >>> with PASS:
  ...     pass

Predicates
++++++++++
Predicates are functors taking arguments and returning True/False
::

  >>> from infi.pyutils.predicates import Predicate
  >>> p = Predicate(lambda obj: obj is None)
  >>> p(None)
  True
  >>> p(1)
  False

AlwaysTrue and AlwaysFalse are available:
::

  >>> from infi.pyutils.predicates import AlwaysTrue, AlwaysFalse
  >>> AlwaysTrue(1)
  True
  >>> AlwaysTrue()
  True
  >>> AlwaysFalse(1)
  False
  >>> AlwaysFalse(343)
  False
  >>> AlwaysFalse()
  False

Identity:
::

   >>> from infi.pyutils.predicates import Identity
   >>> is_none = Identity(None)
   >>> is_none
   <is None>
   >>> is_none(None)
   True
   >>> is_none(1)
   False

Equality:
::

   >>> from infi.pyutils.predicates import Equality
   >>> class NeverEquals(object):
   ...     def __eq__(self, other):
   ...         return False
   >>> equals_to_1 = Equality(1)
   >>> equals_to_1
   < == 1>
   >>> equals_to_1(1)
   True
   >>> equals_to_1(2)
   False
   >>> obj = NeverEquals()
   >>> Equality(obj)(obj) # make sure it's not identity
   False

Attribute checks:
::

   >>> class SomeObject(object):
   ...     pass
   >>> a = SomeObject()
   >>> a.x = 1
   >>> a.y = 2
   >>> a.z = 4
   >>> b = SomeObject()
   >>> b.x = 2
   >>> b.y = 3
   >>> b.z = 4
   >>> from infi.pyutils.predicates import ObjectAttributes
   >>> match = ObjectAttributes(z=4)
   >>> match
   <.z==4>
   >>> match(a)
   True
   >>> match(b)
   True
   >>> match = ObjectAttributes(x=1, y=2)
   >>> match(a)
   True
   >>> match(b)
   False
   >>> ObjectAttributes(missing_attribute=2)(a)
   False

Dictionary items check:
   >>> d = dict(a=1, b=2)
   >>> from infi.pyutils.predicates import DictionaryItems
   >>> match = DictionaryItems(a=1)
   >>> match
   <['a']==1>
   >>>
   >>> match(d)
   True
   >>> match(dict(a=2, b=2))
   False
   >>> match(dict())
   False
   >>> match(dict(b=2))
   False


Logical aggregations are done with And, Or, Not:
::

  >>> from infi.pyutils.predicates import And, Or, Not
  >>> obj = object()
  >>> is_none_or_obj = Or(Identity(obj), Identity(None))
  >>> is_none_or_obj #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
  Or(<is <object object at 0x...>>, <is None>)
  >>> is_none_or_obj(obj)
  True
  >>> is_none_or_obj(None)
  True
  >>> is_none_or_obj(1)
  False
  >>> is_not_none = Not(is_none)
  >>> is_not_none
  <not <is None>>
  >>> is_not_none(None)
  False
  >>> is_not_none(1)
  True

Lazy
----
*infi.pyutils.lazy* presents utilities for lazy computation and caching

cached_property and cached_method
+++++++++++++++++++++++++++++++++

 >>> from infi.pyutils.lazy import cached_property
 >>> class MyClass(object):
 ...     called = False
 ...     @cached_property
 ...     def value(self):
 ...         assert not self.called
 ...         self.called = True
 ...         return 1
 >>> m = MyClass()
 >>> m.value
 1
 >>> m.value
 1

 >>> from infi.pyutils.lazy import cached_method
 >>> class MyClass(object):
 ...     called = False
 ...     @cached_method
 ...     def get_value(self):
 ...         assert not self.called
 ...         self.called = True
 ...         return 1
 >>> m = MyClass()
 >>> m.get_value()
 1
 >>> m.get_value()
 1

Decorator Utilities
-------------------
The *infi.pyutils.decorators* package contains a specially-crafted *wraps* implementation (functools.wraps counterpart) preserving information on the originally wrapped function. It also patches *inspect.getargspec* and IPython's similar mechanisms in order to display proper argument information on wrapped functions. It is therefore recommended to use it instead of the default ones.


Context Utilities
-----------------
*infi.pyutils.contexts* contains *contextmanager*, a drop-in replacement for *contextlib.contextmanager*, using the crafted *wraps* implementation from *decorators*.

Import Utilities
----------------
*infi.pyutils.importing* contains **import_file**, a function for importing a module by its name::

 >>> from infi.pyutils.importing import *
 >>> import tempfile, os
 >>> temp_dir = tempfile.mkdtemp()
 >>> filename = os.path.join(temp_dir, "my_file.py")
 >>> with open(filename, "w") as f:
 ...     _ = f.write("a=2")
 >>> module = import_file(filename)
 >>> module.a
 2

Reference Counters
------------------
*infi.pyutils.reference_counter* is an implementation of a reference counter with dependency support::

 >>> from infi.pyutils.reference_counter import ReferenceCounter
 >>> r = ReferenceCounter()
 >>> r.get_reference_count()
 0
 >>> r.add_reference()
 >>> r.get_reference_count()
 1

Several reference counters can be chained via dependency::

 >>> r1 = ReferenceCounter()
 >>> r2 = ReferenceCounter()
 >>> r1.depend_on_counter(r2)
 >>> r1.add_reference()
 >>> r2.get_reference_count()
 1

Also, as a convenience, if you add a dependency to a counter that already has a nonzero refcount, the dependent counter is automatically increased as well::

 >>> r1 = ReferenceCounter()
 >>> r1.add_reference()
 >>> r2 = ReferenceCounter()
 >>> r1.depend_on_counter(r2)
 >>> r2.get_reference_count()
 1

You can add a callback to be called when the reference count drops to zero::

 >>> r1 = ReferenceCounter()
 >>> def callback(r):
 ...     assert r is r1
 ...     print("called!")
 >>> r1.add_zero_refcount_callback(callback)
 >>> r1.add_reference()
 >>> r1.remove_reference()
 called!

Misc. Utilities
---------------

recursive_getattr
+++++++++++++++++

 >>> from infi.pyutils import recursive_getattr
 >>> class Object(object):
 ...     pass
 >>> a = Object()
 >>> a.b = Object()
 >>> a.b.c = 2
 >>> recursive_getattr(a, 'b.c')
 2
 >>> recursive_getattr(a, 'b.d', 4)
 4

Reprify
+++++++

*Reprify* is intended to force a __repr__/__str__ on objects that don't properly support them::

 >>> from infi.pyutils import Reprify
 >>> class SomeObject(object):
 ...     pass
 >>> some_obj = SomeObject()
 >>> s = Reprify(some_obj, repr='some_repr_here', str='some_str_here')
 >>> repr(s)
 'some_repr_here'
 >>> str(s)
 'some_str_here'

While still preserving the identity and attributes::

 >>> some_obj.attr = 2
 >>> s.attr
 2
 >>> isinstance(s, SomeObject)
 True

Exception Retry Utilities
-------------------------
The *infi.pyutils.retry* package provides a mechanism to easily define when and how to retry a failed operation. It allows you to wrap methods in your class and plug in an error handling strategy (infinite retries, retry N times, expontential decay timeout, etc.) without changing your code.
