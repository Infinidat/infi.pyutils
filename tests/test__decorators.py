from __future__ import print_function
import inspect
from infi.pyutils.decorators import wraps
from .test_utils import TestCase


# inspired from http://docs.python.org/library/functools.html#functools.partial

def my_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print('Calling decorated function')
        return f(*args, **kwds)
    return wrapper

@my_decorator
def example(a, b, c):
    """Docstring"""
    print('Called example function')
    return 1

@my_decorator
@my_decorator
def example_nested(a, b, c):
    """Docstring"""
    return 2


class DecoratorTestCase(TestCase):
    def test__wrapped_attribute_exists(self):
        self.assertIsNotNone(getattr(example, "__wrapped__", None))

    def test__example(self):
        self.assertEquals(example(1, 2, 3), 1)

class GetargspecTest(TestCase):
    def test__argument_names(self):
        for function in (example, example_nested):
            argspec = inspect.getargspec(function)
            self.assertEquals(argspec.args, ['a', 'b', 'c'])

