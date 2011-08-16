from infi.pyutils.mixin import *

def test_install_mixin__simple():
    class A(object):
        pass

    class B(object):
        def foo(self):
            self.a = 1
        
    a = A()
    install_mixin(a, A, B)

    a.foo()
    assert a.a == 1

def test_install_mixin__multiple_inheritence1():
    class A(object):
        pass
    class B(object):
        pass
    class C(object):
        pass
    class D(A, B, C):
        pass
    class E(object):
        def foo(self):
            self.a = 1

    d = D()
    install_mixin(d, D, E)

    d.foo()
    assert d.a == 1
        
def test_install_mixin__multiple_inheritence2():
    class A(object):
        pass
    class B(object):
        pass
    class C(object):
        pass
    class D(A, B, C):
        pass
    class E(object):
        def foo(self):
            self.a = 1

    d = D()
    install_mixin(d, C, E)
    assert issubclass(d.__class__, E)

    d.foo()
    assert d.a == 1

def test_install_mixin__multiple_inheritence3():
    class A(object):
        pass
    class B(object):
        pass
    class C(object):
        pass
    class E(object):
        def foo(self):
            self.a = 2
    class D(A, B, C):
        class D_E(E):
            def foo(self):
                self.a = 1
    d = D()
    install_mixin(d, B, E)
    assert issubclass(d.__class__, E)
    install_mixin(d, D, D.D_E)
    assert issubclass(d.__class__, D.D_E)
    
    d.foo()
    assert d.a == 1
