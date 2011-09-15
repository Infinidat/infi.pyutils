from .decorators import wraps
import platform

_IS_PY3 = platform.python_version() >= '3'

if _IS_PY3:
    from contextlib import _GeneratorContextManager
    def contextmanager(func):
        @wraps(func)
        def helper(*args, **kwds):
            return _GeneratorContextManager(func, *args, **kwds)
        return helper
else:
    from contextlib import GeneratorContextManager as _GeneratorContextManager
    def contextmanager(func):
        @wraps(func)
        def helper(*args, **kwds):
            return _GeneratorContextManager(func(*args, **kwds))
        return helper
