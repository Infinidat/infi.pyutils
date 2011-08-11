import unittest
import inspect
from infi.pyutils.decorators import wraps, contextmanager

# inspired from http://docs.python.org/library/functools.html#functools.partial

def my_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print 'Calling decorated function'
        return f(*args, **kwds)
    return wrapper

@my_decorator
def example(a, b, c):
    """Docstring"""
    print 'Called example function'
    return 1

@my_decorator
@my_decorator
def example_nested(a, b, c):
    """Docstring"""
    return 2

@contextmanager
def example_context_manager(a, b, c):
    """context_manager_docstring"""
    yield 2

class DecoratorTestCase(unittest.TestCase):
    def test__wrapped_attribute_exists(self):
        self.assertIsNotNone(getattr(example, "__wrapped__", None))

    def test__example(self):
        self.assertEquals(example(1, 2, 3), 1)

class ContextmanagerTestCase(unittest.TestCase):
    def test__contextmanager(self):
        self.assertEquals(example_context_manager.__doc__, "context_manager_docstring")
        self.assertEquals(example_context_manager.__name__, "example_context_manager")
        self.assertEquals(inspect.getargspec(example_context_manager).args, ['a', 'b', 'c'])
        with example_context_manager(1, 2, 3) as result:
            pass
        self.assertEquals(result, 2)


class GetargspecTest(unittest.TestCase):
    def test__argument_names(self):
        for function in (example, example_nested):
            argspec = inspect.getargspec(function)
            self.assertEquals(argspec.args, ['a', 'b', 'c'])
            
