import unittest

from infi.pyutils.decorators import wraps

# inspired from http://docs.python.org/library/functools.html#functools.partial

def my_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print 'Calling decorated function'
        return f(*args, **kwds)
    return wrapper

@my_decorator
def example():
    """Docstring"""
    print 'Called example function'
    return 1

class DecoratorTestCase(unittest.TestCase):
    def test_wrapped_attribute_exists(self):
        self.assertNotEquals(getattr(example, "__wrapped__", None), None)

    def test_example(self):
        self.assertEquals(example(), 1)

