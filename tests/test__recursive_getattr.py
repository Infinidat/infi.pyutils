from .test_utils import TestCase
from infi.pyutils import recursive_getattr

class RecursiveGetattrTest(TestCase):
    def setUp(self):
        super(RecursiveGetattrTest, self).setUp()
        self.obj = Object()
        self.obj.a = Object()
        self.obj.a.b = Object()
        self.obj.a.b.value = self.value = Object()
    def test__recursive_getattr_success(self):
        self.assertIs(recursive_getattr(self.obj, 'a.b.value'),
                      self.value)
    def test__recursive_getattr_failure(self):
        with self.assertRaises(AttributeError):
            recursive_getattr(self.obj, 'a.b.bla')
    def test__recursive_getattr_failure_default(self):
        default = Object()
        self.assertIs(
            default,
            recursive_getattr(self.obj, 'a.b.bla', default))

class Object(object):
    pass
