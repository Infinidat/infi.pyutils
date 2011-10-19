from .test_utils import TestCase
from infi.pyutils import EqualByKey, ComparableByKey, HashableByKey

class Equal(EqualByKey):
    def __init__(self, index):
        super(Equal, self).__init__()
        self.key = index
    def _get_key(self):
        return self.key

class Comparable(ComparableByKey):
    def __init__(self, index):
        super(Comparable, self).__init__()
        self.key = index
    def _get_key(self):
        return self.key

class Hashable(HashableByKey):
    def __init__(self, index):
        super(Hashable, self).__init__()
        self.key = index
    def _get_key(self):
        return self.key


class KeyedObjectsTest(TestCase):
    def test__equal_objects(self):
        self.assertTrue( Comparable(1) == Comparable(1))
        self.assertTrue( Comparable(1) != Comparable(0))
        self.assertFalse( Comparable(1) == Comparable(0))
        self.assertFalse( Comparable(1) != Comparable(1))
        with self.assertRaises(TypeError):
            hash(Comparable(1))
    def test__comparable_objects(self):
        self.assertTrue( Comparable(1) >  Comparable(0))
        self.assertFalse(Comparable(1) >  Comparable(2))
        self.assertTrue( Comparable(1) <  Comparable)
        self.assertFalse(Comparable(1) <  Comparable(0))
        self.assertTrue( Comparable(1) >= Comparable(0))
        self.assertTrue( Comparable(1) >= Comparable(1))
        self.assertFalse(Comparable(1) >= Comparable(2))
        with self.assertRaises(TypeError):
            hash(Comparable(1))
    def test__hashable_objects(self):
        self.assertEquals(hash(Hashable("bla")), hash("bla"))


