import functools
from . import test_utils
from collections import defaultdict
from infi.pyutils.lazy import CacheData, TimerCacheData, cached_property, \
    cached_method, populate_cache, cached_function, clear_cache, clear_cached_entry, \
    cached_method_with_custom_cache
import time

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

poll_time = 0.05

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

    def test_caching_method_on_class_instance(self):
        class Foo(object):
            def __init__(self):
                self.counter = 0
            def invalidate_cache(self):
                self._cache["tested_method"].invalidate()
            @cached_method_with_custom_cache(CacheData)
            def tested_method(self):
                self.counter += 1
                return self.counter

        foo = Foo()
        for i in range(1, 5):
            for j in range(5):
                self.assertEquals(foo.tested_method(), i)
            foo.invalidate_cache()

    def test_caching_method_on_external_call(self):
        class Bar(object):
            def __init__(self):
                self.counter = 0
            @cached_method_with_custom_cache(functools.partial(TimerCacheData, poll_time))
            def tested_method(self):
                self.counter += 1
                return self.counter

        bar = Bar()
        for _ in range(3):
            self.assertEquals(bar.tested_method(), 1)

        time.sleep(poll_time + 0.01)
        for _ in range(3):
            self.assertEquals(bar.tested_method(), 2)

    def test_single_class_with_two_caches(self):
        class FooBar(object):
            def __init__(self):
                self.timer = 0
                self.data_counter = 0
            @cached_method_with_custom_cache(functools.partial(TimerCacheData, poll_time))
            def timer_cache(self):
                self.timer += 1
                return self.timer
            @cached_method_with_custom_cache(CacheData)
            def data_cache(self):
                self.data_counter += 1
                return self.data_counter
            def invalidate_cache(self):
                self._cache["data_cache"].invalidate()

        foobar = FooBar()
        for i in range(1, 10):
            for j in range(10):
                self.assertEquals(foobar.data_cache(), i)
                time.sleep(0.01)
            foobar.invalidate_cache()

        for _ in range(3):
            self.assertEquals(foobar.timer_cache(), 1)
            foobar.invalidate_cache()

        time.sleep(poll_time + 0.1)
        for _ in range(3):
            self.assertEquals(foobar.timer_cache(), 2)
            foobar.invalidate_cache()

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
