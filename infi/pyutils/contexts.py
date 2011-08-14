from .decorators import wraps
import contextlib

def contextmanager(func):
    @wraps(func)
    def helper(*args, **kwds):
        return contextlib.GeneratorContextManager(func(*args, **kwds))
    return helper
