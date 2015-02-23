from .test_utils import TestCase
from infi.pyutils.versioned_group import VersionedGroup, VersionedValue, ALL, LATEST, UnboundException

class VersionedValueTest(TestCase):
    def test_non_versioned_value(self):
        versioned_value = VersionedValue('avg', ['AVERAGE', 'average', 'Average'])
        assert versioned_value == 'AVERAGE'
        assert versioned_value == 'average'
        assert versioned_value == 'Average'
        assert versioned_value != 'avg'
        assert versioned_value != 'Median'
        assert versioned_value.get_bound_version() == ALL

    def versioned_value(self):
        return VersionedValue('avg', {'1.0':['AVERAGE', 'average', 'Average'],
                                      '1.0.1':['Average', 'AVG'],
                                      '2.0':['Average', 'avg']})

    def test_versioned_value(self):
        versioned_value = self.versioned_value()
        assert versioned_value.as_version('1.0') == 'average'
        assert versioned_value.as_version('1.0.1') == 'AVG'
        assert versioned_value.as_version('1.0.1') != 'average'
        assert versioned_value.as_version('1.5') != 'average'
        assert versioned_value.as_version('2.0') == 'avg'
        assert versioned_value.as_version('2.0') != 'AVG'
        assert versioned_value.as_version('2.5') == 'avg'
        assert versioned_value.as_version('2.5') != 'AVG'
        assert versioned_value.as_version(LATEST) != 'AVG'


    def test_get_values(self):
        versioned_value = self.versioned_value()
        assert versioned_value.as_version('1.0').get_values() == ['AVERAGE', 'average', 'Average']
        assert versioned_value.as_version('1.0.1').get_values() == ['Average', 'AVG']
        assert versioned_value.as_version('1.5').get_values() == ['Average', 'AVG']
        assert versioned_value.as_version('2.0').get_values() == ['Average', 'avg']
        assert versioned_value.as_version('2.5').get_values() == ['Average', 'avg']

    def test_get_value(self):
        versioned_value = self.versioned_value()
        assert versioned_value.as_version('1.0').get_value() == 'AVERAGE'
        assert versioned_value.as_version('1.0.1').get_value() == 'Average'
        assert versioned_value.as_version('1.5').get_value() == 'Average'
        assert versioned_value.as_version('2.0').get_value() == 'Average'
        assert versioned_value.as_version('2.5').get_value() == 'Average'

    def test_bind_version(self):
        versioned_value = self.versioned_value()
        assert versioned_value.get_bound_version() is None
        versioned_value.bind_to_version('2.5')
        assert versioned_value.get_bound_version() == '2.5'
        assert versioned_value.as_version('2.5').get_values() == ['Average', 'avg']
        assert versioned_value.as_version('2.5').get_value() == 'Average'

    def test_raises_unbound(self):
        versioned_value = self.versioned_value()
        with self.assertRaises(UnboundException):
            versioned_value.get_values()
        with self.assertRaises(UnboundException):
            versioned_value.get_value()
        with self.assertRaises(UnboundException):
            versioned_value.as_version('0.1').get_values()
        with self.assertRaises(UnboundException):
            versioned_value.as_version('0.1').get_value()

    def test_equal_values(self):
        a = VersionedValue('a', {'1.0':['a', 'A'], '2.0':['A']})
        b = VersionedValue('b', {'1.0':['b', 'B'], '2.0':['A']})
        assert a != b
        assert a.as_version('1.0') != a.as_version('2.0')
        assert a.as_version('1.0') == a.as_version('1.5')
        assert a.as_version('2.0') == b.as_version('2.0')
        assert a.as_version('1.0') != b.as_version('1.0')
        assert a.as_version('0.1') == b.as_version('0.1')

class VersionedGroupTest(TestCase):
    def versioned_group(self):
        return VersionedGroup(VersionedValue('one', {'1.0':['One'],
                                                     '2.0':['1', 1, 'One'],
                                                     '2.5':['1', 1]}),
                              VersionedValue('two', {'2.0':['2', 2, 'Two'],
                                                     '2.5':['2', 2]}))

    def test_versioned_group(self):
        versioned_group = self.versioned_group()
        assert versioned_group.one.as_version('2.0').get_values() == ['1', 1, 'One']
        assert versioned_group['one'].as_version('2.0').get_values() == ['1', 1, 'One']
        assert versioned_group.as_version('2.0').one.get_values() == ['1', 1, 'One']
        assert versioned_group.as_version('2.0')['one'].get_values() == ['1', 1, 'One']
        assert versioned_group.as_version('2.0').two.get_values() == ['2', 2, 'Two']
        assert versioned_group.as_version('3.0').two.get_values() == ['2', 2]

        with self.assertRaises(UnboundException):
            versioned_group.two.as_version('1.0').get_value()
        with self.assertRaises(UnboundException):
            versioned_group.as_version('1.0').two.get_value()

    def test_bound(self):
        versioned_group = self.versioned_group()
        versioned_group.bind_to_version('2.0')
        assert versioned_group.one.get_values() == ['1', 1, 'One']
        assert versioned_group['one'].get_values() == ['1', 1, 'One']
        assert versioned_group.one.get_values() == ['1', 1, 'One']
        assert versioned_group['one'].get_values() == ['1', 1, 'One']
        assert versioned_group.two.get_values() == ['2', 2, 'Two']

    def test_find_value(self):
        versioned_group = self.versioned_group()
        assert versioned_group.as_version('1.0').find_value('One').get_values() == ['One']
        assert versioned_group.as_version('2.0').find_value('One').get_values() == ['1', 1, 'One']
        assert versioned_group.as_version('2.0').find_value(1).get_values() == ['1', 1, 'One']
    
        with self.assertRaises(UnboundException):
            versioned_group.find_value('One')
        with self.assertRaises(UnboundException):
            versioned_group.as_version('1.0').find_value(1)
