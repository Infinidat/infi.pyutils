
import functools
import inspect

def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'), updated=('__dict__',)):
    """ a convenience function on top of functools.wraps:

    - adds the original function to the wrapped function as __wrapped__ attribute."""
    func = functools.wraps(wrapped, assigned, updated)
    setattr(wrapped, "__wrapped__", wrapped)
    return func

def getargspec(func):
    """calls inspect's getargspec with func.__wrapped__ if exists, else with func"""
    func = getattr(func, "__wrapped__", func)
    return inspect._getargspec(func)

def mockeypatch_inspect():
    """applies getarspec monkeypatch on inspect"""
    setattr(inspect, "_getargspec", inspect.getargspec)
    setattr(inspect, "getargspec", getargspec)
    setattr(inspect, "__patched_by_infi__", True)

if not getattr(inspect, "__patched_by_infi__", False):
    mockeypatch_inspect()

