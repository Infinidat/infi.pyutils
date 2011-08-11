import contextlib
import functools
import inspect

def contextmanager(func):
    @wraps(func)
    def helper(*args, **kwds):
        return contextlib.GeneratorContextManager(func(*args, **kwds))
    return helper

def wraps(wrapped):
    """ a convenience function on top of functools.wraps:

    - adds the original function to the wrapped function as __wrapped__ attribute."""
    def new_decorator(f):
        returned = functools.wraps(wrapped)(f)
        returned.__wrapped__ = wrapped
        return returned
    return new_decorator

def inspect_getargspec_patch(func):
    """calls inspect's getargspec with func.__wrapped__ if exists, else with func"""
    return inspect._infi_patched_getargspec(_get_innner_func(func))
def ipython_getargspec_patch(func):
    return _ipython_inspect_module._infi_patched_getargspec(_get_innner_func(func))

def _get_innner_func(f):
    while True:
        wrapped = getattr(f, "__wrapped__", None)
        if wrapped is None:
            return f
        f = wrapped

_PATCHED_NAME_PREFIX = "_infi_patched_"

def monkey_patch(module, name, replacement):
    original_name = _PATCHED_NAME_PREFIX + name
    if getattr(module, original_name, None) is None:
        setattr(module, original_name, getattr(module, name))
        setattr(module, name, replacement)

monkey_patch(inspect, "getargspec", inspect_getargspec_patch)

_ipython_inspect_module = None
try:
    # ipython 0.11
    from IPython.core import oinspect as _ipython_inspect_module
except ImportError:
    try:
        # ipython 0.10.2
        from IPython import OInspect as _ipython_inspect_module
    except ImportError:
        pass

if _ipython_inspect_module is not None:
    monkey_patch(_ipython_inspect_module, "getargspec", ipython_getargspec_patch)
