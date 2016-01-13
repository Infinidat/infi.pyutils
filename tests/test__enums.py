import copy, pickle
from infi.pyutils.enums import Enum, Value, ALL, UnboundException
from .test_utils import TestCase

LATEST = '1000000.0'

class VersionedValueTest(TestCase):
    def test_non_versioned_value(self):
        versioned_value = Value('avg', ['AVERAGE', 'average', 'Average'])
        assert versioned_value == 'avg' # key is in non versioned value for backward compat
        assert versioned_value == 'AVERAGE'
        assert versioned_value == 'average'
        assert versioned_value == 'Average'
        assert versioned_value != 'Median'
        assert versioned_value.get_bound_version() == ALL

    def versioned_value(self):
        return Value('avg', {'1.0':['AVERAGE', 'average', 'Average'],
                             '1.0.1':['Average', 'AVG'],
                             '2.0':['Average', 'avg']})

    def test_versioned_value(self):
        versioned_value = self.versioned_value()
        assert versioned_value.as_version('1.0') != 'avg' # key is not in versioned value
        assert versioned_value.as_version('1.0') == 'average'
        assert versioned_value.as_version('1.0.1') == 'AVG'
        assert versioned_value.as_version('1.0.1') != 'median'
        assert versioned_value.as_version('1.5') != 'median'
        assert versioned_value.as_version('2.0') == 'avg'
        assert versioned_value.as_version('2.0') != 'median'
        assert versioned_value.as_version('2.5') == 'avg'
        assert versioned_value.as_version('2.5') != 'median'
        assert versioned_value.as_version(LATEST) == 'avg'
        assert versioned_value.as_version(LATEST) != 'median'


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
        assert versioned_value.get_bound_version() == ALL
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
        a = Value('a', {'1.0':['a', 'A'], '2.0':['A'], '3.0':['C']})
        b = Value('b', {'1.0':['b', 'B'], '2.0':['A']})
        assert a.as_version('1.0') == a.as_version('2.0')
        assert a.as_version('1.0') != a.as_version('3.0')
        assert a.as_version('1.0') == a.as_version('1.5')
        assert a.as_version('2.0') == b.as_version('2.0')
        assert a.as_version('1.0') != b.as_version('1.0')
        assert a.as_version('0.1') == b.as_version('0.1')

class VersionedEnumTest(TestCase):
    def versioned_enum(self):
        return Enum(Value('one', {'1.0':['One'],
                                  '2.0':['1', 1, 'One'],
                                  '2.5':['1', 1]}),
                    Value('two', {'2.0':['2', 2, 'Two'],
                                  '2.5':['2', 2]}))

    def test_versioned_enum(self):
        versioned_enum = self.versioned_enum()
        assert versioned_enum.one.as_version('2.0').get_values() == ['1', 1, 'One']
        assert versioned_enum['one'].as_version('2.0').get_values() == ['1', 1, 'One']
        assert versioned_enum.as_version('2.0').one.get_values() == ['1', 1, 'One']
        assert versioned_enum.as_version('2.0')['one'].get_values() == ['1', 1, 'One']
        assert versioned_enum.as_version('2.0').two.get_values() == ['2', 2, 'Two']
        assert versioned_enum.as_version('3.0').two.get_values() == ['2', 2]

        with self.assertRaises(UnboundException):
            versioned_enum.two.as_version('1.0').get_value()
        with self.assertRaises(UnboundException):
            versioned_enum.as_version('1.0').two.get_value()

    def test_bound(self):
        versioned_enum = self.versioned_enum()
        versioned_enum.bind_to_version('2.0')
        assert versioned_enum.one.get_values() == ['1', 1, 'One']
        assert versioned_enum['one'].get_values() == ['1', 1, 'One']
        assert versioned_enum.one.get_values() == ['1', 1, 'One']
        assert versioned_enum['one'].get_values() == ['1', 1, 'One']
        assert versioned_enum.two.get_values() == ['2', 2, 'Two']

    def test_get(self):
        versioned_enum = self.versioned_enum()
        assert versioned_enum.as_version('1.0').get('One').get_values() == ['One']
        assert versioned_enum.as_version('2.0').get('One').get_values() == ['1', 1, 'One']
        assert versioned_enum.as_version('2.0').get(1).get_values() == ['1', 1, 'One']

        with self.assertRaises(UnboundException):
            versioned_enum.get('One')
        with self.assertRaises(UnboundException):
            versioned_enum.as_version('1.0').get(1)


class EnumTestCase(TestCase):
    """ The old enum behavior, we need to keep this working for backwards compatibility """

    def setUp(self):
        self.enum = Enum("String", Value("VALUE", aliases=["FIRST_ALIAS", "SECOND_ALIAS"]))

    def test__is_value(self):
        for e in self.enum:
            self.assertIsInstance(e, Value)

    def test__equals(self):
        self.assertEquality(self.enum.string, "String")
        self.assertEquality(self.enum.string, "STRING")
        self.assertEquality(self.enum.value, "VALUE")
        self.assertInequality(self.enum.value, self.enum.string)
        self.assertInequality(self.enum.string, "VALUE")

    def test__aliases(self):
        for alias in ("value", "Value", "VALUE", "FIRST_ALIAS", "SECOND_ALIAS", "second_alias"):
            self.assertEquality(self.enum.value, alias)
            self.assertEquality(Value(alias), self.enum.value)
            self.assertInequality(alias + "x", self.enum.value)

    def test__aliased_values(self):
        aliased_value = Value("aliased", aliases=[self.enum.value, self.enum.string])
        for alias in ("value", "Value", "VALUE", "FIRST_ALIAS", "SECOND_ALIAS", "second_alias", "String", self.enum.value, self.enum.string):
            self.assertEquality(aliased_value, alias)
            self.assertEquality(Value(alias), aliased_value)
            self.assertInequality(str(alias) + "x", aliased_value)

    def test__in(self):
        self.assertIn("String", self.enum)
        self.assertIn("VALUE", self.enum)
        self.assertIn("FIRST_ALIAS", self.enum)
        self.assertIn("SECOND_ALIAS", self.enum)

    def test__alias_is_not_a_value(self):
        self.assertRaises(AttributeError, getattr, self.enum, "first_alias")

    def test__iteration(self):
        self.assertEquality(list(self.enum), ["String", "VALUE"])

    def test__get(self):
        self.assertEqual(self.enum.value, self.enum.get("VALUE"))
        self.assertEqual(self.enum.value, self.enum.get("Value"))
        self.assertEqual(self.enum.value, self.enum.get("FIRST_ALIAS"))
        self.assertEqual(self.enum.value, self.enum.get("first_alias"))
        self.assertRaises(AttributeError, self.enum.get, "illegal")

    def test__get_attribute(self):
        self.assertEqual(self.enum.string, "String")
        with self.assertRaises(AttributeError):
            self.enum.fake_value
        with self.assertRaises(AttributeError):
            self.enum._fake_value

    def test__deepcopy(self):
        my_dict = {'a': 1, 'b': Enum('a', 'b', 'c', 'd')}
        dict_copy = copy.deepcopy(my_dict)
        self.assertEqual(my_dict['a'], dict_copy['a'])
        self.assertEqual(list(my_dict['b']), list(dict_copy['b']))

    def test__get_value_name(self):
        input_values = ["CamelCase", "lower_case", "UPPER_CASE"]
        enum = Enum(*input_values)
        self.assertEqual([val.get_name() for val in enum], input_values)
        self.assertEqual([str(val) for val in enum], [val.upper() for val in input_values])

    def test__picklable(self):
        self.assertTrue(self.enum == pickle.loads(pickle.dumps(self.enum)))

    def assertEquality(self, a, b):
        msg = "Equality check for {0!r} == {1!r} failed".format(a, b)
        self.assertTrue(a == b, msg)
        self.assertTrue(b == a, msg)
        self.assertFalse(a != b, msg)
        self.assertFalse(b != a, msg)

    def assertInequality(self, a, b):
        msg = "Inequality check for {0!r} != {1!r} failed".format(a, b)
        self.assertFalse(a == b, msg)
        self.assertFalse(b == a, msg)
        self.assertTrue(a != b, msg)
        self.assertTrue(b != a, msg)
