import itertools
import functools
from .test_utils import TestCase
from infi.pyutils import iterate
from infi.pyutils.reference_counter import (
    ReferenceCounter,
    InvalidReferenceCount,
    )

class ReferenceCounterTest(TestCase):
    def test__reference_counter(self):
        self.value = False
        r = MyReferenceCounter(functools.partial(setattr, self, "value"))
        self.assertFalse(self.value)
        r.add_reference()
        self.assertTrue(self.value)
        self.assertEquals(r.get_reference_count(), 1)
        r.add_reference()
        self.assertTrue(self.value)
        self.assertEquals(r.get_reference_count(), 2)
        r.remove_reference()
        self.assertTrue(self.value)
        self.assertEquals(r.get_reference_count(), 1)
        r.remove_reference()
        self.assertFalse(self.value)
        self.assertEquals(r.get_reference_count(), 0)
        with self.assertRaises(InvalidReferenceCount):
            r.remove_reference()
        self.assertFalse(self.value)
        self.assertEquals(r.get_reference_count(), 0)
        with r.get_reference_context():
            self.assertTrue(self.value)
            self.assertEquals(r.get_reference_count(), 1)
        self.assertFalse(self.value)
        self.assertEquals(r.get_reference_count(), 0)
        try:
            with r.get_reference_context():
                raise Exception()
        except Exception:
            pass
        self.assertFalse(self.value)
        self.assertEquals(r.get_reference_count(), 0)
    def test__reference_counter_exception_while_add_reference(self):
        refcounter = MyReferenceCounter(raise_on_addref=True)
        with self.assertRaises(MyException):
            refcounter.add_reference()
        self.assertEquals(refcounter.get_reference_count(), 0)
    def test__reference_counter_exception_while_remove_reference(self):
        refcounter = MyReferenceCounter(raise_on_decref=True)
        refcounter.add_reference()
        with self.assertRaises(MyException):
            refcounter.remove_reference()
        self.assertEquals(refcounter.get_reference_count(), 1)
    def test__reference_drop_callback(self):
        refcounter = MyReferenceCounter()
        self.called = False
        def _callback(r):
            self.assertIs(r, refcounter)
            self.called = True
        refcounter.add_zero_refcount_callback(_callback)
        refcounter.add_reference()
        refcounter.add_reference()
        self.assertFalse(self.called)
        refcounter.remove_reference()
        self.assertFalse(self.called)
        refcounter.remove_reference()
        self.assertTrue(self.called)
class DependentReferenceCounterTest(TestCase):
    def test__dependent_reference_counter(self):
        ref1 = ReferenceCounter()
        ref2 = ReferenceCounter()
        ref1.depend_on_counter(ref2)
        self.assertEquals(ref1.get_reference_count(), 0)
        self.assertEquals(ref2.get_reference_count(), 0)
        ref1.add_reference()
        self.assertEquals(ref1.get_reference_count(), 1)
        self.assertEquals(ref2.get_reference_count(), 1)
        ref1.add_reference()
        self.assertEquals(ref1.get_reference_count(), 2)
        self.assertEquals(ref2.get_reference_count(), 1)
        ref1.remove_reference()
        self.assertEquals(ref1.get_reference_count(), 1)
        self.assertEquals(ref2.get_reference_count(), 1)
        ref1.remove_reference()
        self.assertEquals(ref1.get_reference_count(), 0)
        self.assertEquals(ref2.get_reference_count(), 0)
    def test__dependent_reference_counter_after_addref(self):
        num_refs = 10
        ref1 = ReferenceCounter()
        ref2 = ReferenceCounter()
        for i in range(num_refs - 1):
            ref1.add_reference()
        ref1.depend_on_counter(ref2)
        self.assertEquals(ref1.get_reference_count(), num_refs - 1)
        self.assertEquals(ref2.get_reference_count(), 1)
        ref1.add_reference()
        self.assertEquals(ref1.get_reference_count(), num_refs)
        for iteration, _ in iterate(range(num_refs)):
            ref1.remove_reference()
            if iteration.last:
                self.assertEquals(ref2.get_reference_count(), 0)
            else:
                self.assertEquals(ref2.get_reference_count(), 1)

class DependentReferenceCounterWithExceptionTest(TestCase):
    def setUp(self):
        super(DependentReferenceCounterWithExceptionTest, self).setUp()
        self.master = MyReferenceCounter()
        self.slaves = [MyReferenceCounter() for i in range(10)]
        for slave in self.slaves:
            self.master.depend_on_counter(slave)
    def test__master_addref_exception_does_not_addref_slaves(self):
        self.master.raise_on_addref = True
        with self.assertRaises(MyException):
            self.master.add_reference()
        self.assertAllRefs(0)

    def test__master_decref_exception_does_not_decref_slaves(self):
        self.master.raise_on_decref = True
        self.master.add_reference()
        self.assertAllRefs(1)
        with self.assertRaises(MyException):
            self.master.remove_reference()
        self.assertAllRefs(1)

    def assertAllRefs(self, value):
        for index, counter in enumerate(itertools.chain([self.master], self.slaves)):
            self.assertEquals(counter.get_reference_count(), value)


class MyException(Exception):
    pass

class MyReferenceCounter(ReferenceCounter):
    def __init__(self, callback=None, raise_on_addref=False, raise_on_decref=False):
        super(MyReferenceCounter, self).__init__()
        self.callback = callback
        self.raise_on_addref = raise_on_addref
        self.raise_on_decref = raise_on_decref
    def _on_reference_first_added(self):
        if self.raise_on_addref:
            raise MyException()
        if self.callback is not None:
            self.callback(True)
    def _on_reference_last_dropped(self):
        if self.raise_on_decref:
            raise MyException()
        if self.callback is not None:
            self.callback(False)

