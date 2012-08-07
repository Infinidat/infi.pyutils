import sys
import traceback
import unittest
import time
from mock import patch, Mock

from infi.pyutils.retry import Retryable, retry_func, retry_method, retry_func_except_for, retry_func_on
from infi.pyutils.retry import ALWAYS_RETRY_STRATEGY, WaitAndRetryStrategy, BinaryExponentialDelayRetryStrategy
from infi.pyutils.retry import AnyRetryStrategy, InSetRetryStrategy

class RetryTestCase(unittest.TestCase):
    def test__default_retry(self):
        class Foo(Retryable):
            @retry_method
            def foo(self):
                raise Exception("I believe I can fly")

        f = Foo()
        try:
            f.foo()
        except:
            etype, e, tb = sys.exc_info()
            self.assertEquals("I believe I can fly", str(e))
            self.assertEquals(3, len(traceback.format_tb(tb)))
        else:
            fail()

    @patch('infi.pyutils.retry.time.sleep')
    def test__wait_and_retry(self, sleep):
        class Foo(Retryable):
            retry_strategy = WaitAndRetryStrategy(max_retries=4, wait=1)
            counter = 0

            @retry_method
            def foo(self):
                self.counter = self.counter + 1
                if self.counter <= 3:
                    raise Exception("ha ha")

        f = Foo()
        f.foo()
        self.assertEquals(4, f.counter)
        self.assertEquals(3, sleep.call_count)

        sleep.reset_mock()
        f = Foo()
        f.retry_strategy = WaitAndRetryStrategy(max_retries=3, wait=0)
        try:
            f.foo()
            fail()
        except Exception:
            self.assertEquals(2, sleep.call_count)

    def test__always_retry_func(self):
        class MyException(Exception):
            pass

        counter = []

        @retry_func_except_for(MyException)
        def my_func(counter):
            counter.append(1)
            if len(counter) == 10:
                raise MyException()
            elif len(counter) < 5:
                raise Exception("be")
            else:
                raise BaseException("ba")

        try:
            my_func(counter)
        except MyException:
            self.assertEquals(10, len(counter))
        else:
            fail()

    def test__always_retry_method(self):
        class Foo(Retryable):
            counter = 0
            retry_strategy = ALWAYS_RETRY_STRATEGY

            @retry_method
            def foo(self):
                self.counter = self.counter + 1
                if self.counter < 0:
                    raise Exception("error")

        f = Foo()
        f.foo()

    def test__retry_func_on(self):
        class MyException(Exception):
            pass

        class MyException2(Exception):
            pass

        counter = []
        @retry_func_on(MyException)
        def foo(counter):
            counter.append(1)
            if len(counter) == 3:
                raise MyException2()
            raise MyException()

        try:
            foo(counter)
            fail()
        except MyException2:
            self.assertEquals(3, len(counter))

        @retry_func_on(MyException)
        def foo():
            pass

        foo()

    @patch('infi.pyutils.retry.time.sleep')
    def test__binary_exponential_delay_retry_strategy(self, sleep):
        @retry_func(BinaryExponentialDelayRetryStrategy(0.1, 1, retry_on_delay_limit=False))
        def foo(n):
            if n == 1:
                raise Exception("boo")

        foo(2)

        try:
            foo(1)
            fail()
        except Exception:
            # 0.1, 0.2, 0.4, 0.8
            self.assertEquals(4, sleep.call_count)

        sleep.reset_mock()

        try:
            foo(1)
            fail()
        except Exception:
            self.assertEquals(0, sleep.call_count)

        sleep.reset_mock()
        foo(3)
        try:
            foo(1)
            fail()
        except Exception:
            # 0.1, 0.2, 0.4, 0.8
            self.assertEquals(4, sleep.call_count)

    def test__any_retry_strategy(self):
        class MyException(Exception):
            pass
        class MyException2(Exception):
            pass
        class MyException3(Exception):
            pass

        s1 = InSetRetryStrategy([ MyException ], True)
        s2 = InSetRetryStrategy([ MyException2 ], True)

        s = AnyRetryStrategy([ s1, s2 ])

        @retry_func(s)
        def foo(counter):
            counter.pop()
            if len(counter) == 0:
                raise MyException()
            elif len(counter) == 1:
                raise MyException2()
            elif len(counter) == 2:
                raise MyException3()

        foo([1, 1, 1, 1])

        try:
            foo([ 1 ])
            fail()
        except MyException:
            pass

        try:
            foo([ 1, 1 ])
            fail()
        except MyException2:
            pass

        try:
            foo([ 1, 1, 1 ])
            fail()
        except MyException2:
            pass
