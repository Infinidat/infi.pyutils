import unittest
import inspect
from infi.pyutils.contexts import contextmanager

@contextmanager
def example_context_manager(a, b, c):
    """context_manager_docstring"""
    yield 2

class ContextmanagerTestCase(unittest.TestCase):
    def test__contextmanager(self):
        self.assertEquals(example_context_manager.__doc__, "context_manager_docstring")
        self.assertEquals(example_context_manager.__name__, "example_context_manager")
        self.assertEquals(inspect.getargspec(example_context_manager).args, ['a', 'b', 'c'])
        with example_context_manager(1, 2, 3) as result:
            pass
        self.assertEquals(result, 2)

