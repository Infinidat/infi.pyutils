Overview
========
*infi.reflection* is a set of utilities for various introspection and reflection tasks in Python.

Features
========

Method Map
----------

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

  >>> from infi.reflection.method_map import MethodMap
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
