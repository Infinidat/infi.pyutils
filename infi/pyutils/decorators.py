import functools
import inspect

def wraps(wrapped):
    """ a convenience function on top of functools.wraps:

    - adds the original function to the wrapped function as __wrapped__ attribute."""
    def new_decorator(f):
        returned = functools.wraps(wrapped)(f)
        returned.__wrapped__ = wrapped
        return returned
    return new_decorator

def getargspec(func):
    """calls inspect's getargspec with func.__wrapped__ if exists, else with func"""
    wrapped = getattr(func, "__wrapped__", None)
    if wrapped is not None:
        return getargspec(wrapped)
    return inspect._getargspec(func)

def monkeypatch_inspect():
    """applies getarspec monkeypatch on inspect"""
    inspect._getargspec = inspect.getargspec
    inspect.getargspec = getargspec
    inspect.__patched_by_infi__ = True

if not getattr(inspect, "__patched_by_infi__", False):
    monkeypatch_inspect()

