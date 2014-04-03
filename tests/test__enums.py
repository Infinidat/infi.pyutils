from infi.pyutils.enums import Enum, Value
from .test_utils import TestCase

class EnumTestCase(TestCase):
    def setUp(self):
        self.enum = Enum("String", Value("VALUE", aliases = ["FIRST_ALIAS", "SECOND_ALIAS"]))
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
    def test__str_repr(self):
        for func in (str, repr):
            self.assertEquality(func(self.enum.string), "STRING")
    def test__get(self):
        self.assertEqual(self.enum.value, self.enum.get("VALUE"))
        self.assertEqual(self.enum.value, self.enum.get("Value"))
        self.assertEqual(self.enum.value, self.enum.get("FIRST_ALIAS"))
        self.assertEqual(self.enum.value, self.enum.get("first_alias"))
        self.assertRaises(AttributeError, self.enum.get, "illegal")
    def test_get_value_name(self):
        input_values = ["CamelCase", "lower_case", "UPPER_CASE"]
        enum = Enum(*input_values)
        self.assertEqual([val.get_name() for val in enum], input_values)
        self.assertEqual([str(val) for val in enum], [val.upper() for val in input_values])
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
