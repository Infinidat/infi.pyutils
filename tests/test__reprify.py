from .test_utils import TestCase
from infi.pyutils import Reprify

class OriginalObject(object):
    def __init__(self):
        super(OriginalObject, self).__init__()
        self.public_attr = 54321
        self._private_attr = 12345
    def method(self):
        return 666
    @classmethod
    def classmethod(cls):
        return 777
    @staticmethod
    def staticmethod():
        return 888
    def __repr__(self):
        raise NotImplementedError() # pragma: no cover
    def __str__(self):
        raise NotImplementedError() # pragma: no cover

class ReprifyTest(TestCase):
    def setUp(self):
        super(ReprifyTest, self).setUp()
        self.original_object = OriginalObject()
        self.REPR = "some repr here"
        self.STR  = "some str here"
        self.obj = Reprify(self.original_object, str=self.STR, repr=self.REPR)
    def test__repr(self):
        self.assertEquals(repr(self.obj), self.REPR)
    def test__str(self):
        self.assertEquals(str(self.obj), self.STR)
    def test__getattr(self):
        self.assertEquals(self.obj.public_attr, self.original_object.public_attr)
        self.assertEquals(self.obj._private_attr, self.original_object._private_attr)
        with self.assertRaises(AttributeError):
            self.obj.nonexistent_attr
    def test__method_calls(self):
        for method_name in ('method', 'classmethod', 'staticmethod'):
            self.assertEquals(
                getattr(self.obj, method_name)(),
                getattr(self.original_object, method_name)(),
                "%r not relayed" % (method_name,),
                )
    def test__isinstance(self):
        self.assertTrue(isinstance(self.obj, OriginalObject))

