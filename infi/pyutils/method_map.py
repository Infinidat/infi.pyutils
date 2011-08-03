import functools
from .functors import Identity
from types import MethodType

class MethodMap(object):
    def __init__(self, decorator=Identity):
        super(MethodMap, self).__init__()
        self._map = {}
        self._decorate = decorator
    def registering(self, key):
        return functools.partial(self.register, key)
    def register(self, key, value):
        self._map[key] = self._decorate(value)
        return value
    def __get__(self, instance, owner):
        return Binder(self._map, instance)

_NOTHING = object()

class Binder(object):
    def __init__(self, map, instance):
        super(Binder, self).__init__()
        self._map = map
        self._instance = instance
    def get(self, key, default=None):
        if key not in self._map:
            return default
        function = self._map[key]
        if isinstance(function, staticmethod):
            return function.__func__
        if isinstance(function, classmethod):
            returned_self = self._instance
            function = function.__func__
        else:
            returned_self = self._instance.__class__
        return MethodType(
            function,
            returned_self,
            self._instance.__class__
            )
        return self._map[key]
    def __getitem__(self, key):
        returned = self.get(key, _NOTHING)
        if returned is _NOTHING:
            raise LookupError(key)
        return returned

