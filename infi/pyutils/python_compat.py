import types
import platform

_PYTHON_VERSION = platform.python_version()
_IS_PYTHON_3 = _PYTHON_VERSION >= '3'
_IS_BELOW_PYTHON_2_7 = _PYTHON_VERSION < '2.7'

def get_underlying_function(f):
    if _IS_BELOW_PYTHON_2_7 and (isinstance(f, classmethod) or isinstance(f, staticmethod)):
        return _get_underlying_classmethod_function(f)
    return f.__func__

def _get_underlying_classmethod_function(f):
    """Hack for older python versions..."""
    class TemporaryClass(object):
        func = f
    if isinstance(f, staticmethod):
        return TemporaryClass.func
    return TemporaryClass.func.im_func

if _IS_PYTHON_3:
    iteritems = dict.items
    xrange = range
else:
    iteritems = dict.iteritems
    from __builtin__ import xrange

if _IS_PYTHON_3:
    create_bound_method = types.MethodType
else:
    def create_bound_method(func, self):
        return types.MethodType(func, self, type(self))
