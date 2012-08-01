import time
from . import test_utils
from collections import defaultdict
from infi.pyutils.lazy import cached_property, cached_method, populate_cache, cached_function
from infi.pyutils.lazy import clear_cache, clear_cached_entry

class Subject(object):
    def __init__(self):
        super(Subject, self).__init__()
        self._counter = 0
        self._counters = defaultdict(lambda: defaultdict(int))
    @cached_property
    def prop(self):
        self._counter += 1
        return self._counter
    def orig_method(self, value):
        """some docstring"""
        self._counters['orig_method'][value] += 1
        return self._counters['orig_method'][value]
    @cached_method
    def cached_method_3(self, value):
        self._counter += 1
        return self._counter
    @cached_method
    def cached_method_4(self):
        self._counter = 1
        return self._counter

    cached_method_1 = cached_method(orig_method)
    cached_method_2 = cached_method(orig_method)

class TestCase(test_utils.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.subject = Subject()

class CachedPropertyTest(TestCase):
    def test__cached_property(self):
        self.assertEquals(self.subject.prop, 1)
    def test__clear_cache(self):
        self.assertEquals(self.subject.prop, 1)
        clear_cache(self.subject)
        self.assertEquals(self.subject.prop, 2)
    def test__populate_cache(self):
        self.assertEquals(self.subject._counter, 0)
        populate_cache(self.subject)
        self.assertEquals(self.subject._counter, 1)

class CachedMethodTest(TestCase):
    def test__doc(self):
        self.assertTrue(self.subject.cached_method_1.__doc__ == self.subject.cached_method_2.__doc__ == self.subject.orig_method.__doc__)
    def test__name(self):
        self.assertTrue(self.subject.cached_method_2.__name__ == self.subject.cached_method_2.__name__ == self.subject.orig_method.__name__)
    def test__cached_method(self):
        self.assertEquals(self.subject.cached_method_1(1), 1)
        self.assertEquals(self.subject.cached_method_1(1), 1)
        self.assertEquals(self.subject.cached_method_2(1), 2)
    def test__clear_cache(self):
        self.assertEquals(self.subject.cached_method_1(1), 1)
        self.assertEquals(self.subject.cached_method_1(1), 1)
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_1(1), 2)
    def test__args(self):
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_3(1), 1)
        self.assertEquals(self.subject.cached_method_3(1), 1)
        self.assertEquals(self.subject.cached_method_3(2), 2)
        self.assertEquals(self.subject.cached_method_3(2), 2)
    def test__mutable_args(self):
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_3([1]), 1)
        self.assertEquals(self.subject.cached_method_3([1]), 2)
    def test__kwargs(self):
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_3(value=1), 1)
        self.assertEquals(self.subject.cached_method_3(value=1), 1)
        self.assertEquals(self.subject.cached_method_3(value=2), 2)
        self.assertEquals(self.subject.cached_method_3(value=2), 2)
    def test__mutable_kwargs(self):
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_3(value=[1]), 1)
        self.assertEquals(self.subject.cached_method_3(value=[1]), 2)
    def test__no_args_and_kwargs(self):
        clear_cache(self.subject)
        self.assertEquals(self.subject.cached_method_4(), 1)
        self.assertEquals(self.subject.prop, 2)
        self.assertEquals(self.subject.cached_method_4(), 1)
        clear_cache(self.subject)

@cached_function
def func():
    return time.time()

class CachedFunctionTest(TestCase):
    def test_cache_works(self):
        before = func()
        after = func()
        self.assertEqual(before, after)

    def test_clear_cache_works(self):
        before = func()
        clear_cache(func)
        after = func()
        self.assertNotEqual(before, after)

    def test_cache_works_after_cleanup(self):
        first = func()
        clear_cache(func)
        second = func()
        third = func()
        self.assertNotEqual(first, second)
        self.assertEqual(second, third)

class Counter(object):
    def __init__(self):
        super(Counter, self).__init__()
        self._count = 0

    @cached_method
    def count(self):
        self._count += 1
        return self._count

    @cached_method
    def sum(self, num):
        return num + self._count


class ClearCachedEntryTest(TestCase):
    def test_on_instance_method__no_args(self):
        counter = Counter()
        method = counter.count
        self.assertEquals(method(), 1)
        self.assertEquals(method(), 1)
        clear_cached_entry(method)
        self.assertEquals(method(), 2)

    def test_on_instance_method__with_args(self):
        counter = Counter()
        method = counter.sum
        self.assertEquals(method(1), 1)
        counter.count()
        self.assertEquals(method(1), 1)
        clear_cached_entry(method, 1)
        self.assertEquals(method(1), 2)

    def test_on_function__with_args(self):
        count = 0
        @cached_function
        def sum(num):
            return num + count
        self.assertEquals(sum(1), 1)
        self.assertEquals(sum(1), 1)
        count = 2
        self.assertEquals(sum(1), 1)
        clear_cached_entry(sum, 1)
        self.assertEquals(sum(1), 3)

    def test_clear_cached_entry_with_mismatching_args_does_nothing(self):
        counter = Counter()
        method = counter.sum
        self.assertEquals(method(1), 1)
        counter.count()
        self.assertEquals(method(1), 1)
        clear_cached_entry(method, 3)
        self.assertEquals(method(1), 1)

