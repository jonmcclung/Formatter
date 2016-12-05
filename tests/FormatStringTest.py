from collections import namedtuple
from unittest import TestCase

from EqualityByValue import EqualityByValue
from Formatter import Formatter
from Lexer import Lexer
from Node import FieldName, Attribute, Index, FormatString, Replacement
from Parser import Parser
from Token import Token
from TokenEnum import TokenEnum


class Foo:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class FieldNameTest(TestCase):
    def test_attribute(self):
        attribute = Attribute('x')
        foo = Foo(5, 10)
        self.assertEqual(foo.x, attribute.get(foo))
        self.assertEqual(foo.y, Attribute('y').get(foo))

    def test_index(self):
        index = Index(4)
        self.assertEqual(5, index.get(range(1, 10)))

    def test_field_name_0(self):
        attribute = Attribute('y')
        foo = Foo(5, [23, 4, 1])
        index = Index(2)
        field_name = FieldName('foo', [attribute, index])
        self.assertEqual(1, field_name.eval(foo=foo))

    def test_field_name_1(self):
        x = Attribute('x')
        y = Attribute('y')
        foo_0 = Foo(4, 5)
        foo_1 = Foo(6, 9)
        foo_2 = Foo([foo_0, foo_1], 10)
        foo_3 = Foo(foo_2, [23, 4, 1])
        self.assertEqual(1, FieldName(0, [Attribute('y'), Index(2)]).eval(foo_3))
        self.assertEqual(10, FieldName(
            4,
            [Attribute('x'), Attribute('y')]).eval(0, 1, 2, 3, foo_3))

    def test_wrapper(self):
        @EqualityByValue
        class Foo:
            def __init__(self, x):
                self.x = x

        self.assertEqual(Foo([1, 2]), Foo([1, 2]))

    def test_format_string_0(self):
        foo = Foo([0, 2], 5)
        format_str = '{0.x[1]}'
        lexer = Lexer(format_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        format_string = parser.parse()
        should_be_equal = FormatString([Replacement(field_name=FieldName(0, [Attribute('x'), Index(1)]))])
        self.assertEqual(
            format_string,
            FormatString([Replacement(field_name=FieldName(0, [Attribute('x'), Index(1)]))]))

    def test_formatter_0(self):
        foo = Foo([0, 2], 5)
        format_str = '{0.x[1]}'
        self.assertEqual(Formatter.format(format_str, foo), '2')

    def test_formatter_1(self):
        foo = Foo(range(20), 5)
        format_str = '{0O10.x[0b10]}'
        self.assertEqual(Formatter.format(format_str, 0, 1, 2, 3, 4, 5, 6, 7, foo), '2')

    def test_formatter_2(self):
        matrix = [[[[[[4]]]]]]
        format_str = 'abracashow {{ {matrix_[0][0][0][0][0][0]}'
        self.assertEqual(Formatter.format(format_str, matrix_=matrix), 'abracashow { 4')

    def test_formatter_3(self):
        format_str = 'milk and {}'
        self.assertEqual(Formatter.format(format_str, 'eggs'), 'milk and eggs')

    def test_formatter_4(self):
        format_str = 'milk and {!s:}'
        self.assertEqual(Formatter.format(format_str, 'eggs'), 'milk and eggs')

    def test_formatter_5(self):
        format_str = 'milk and {!s:#}'
        try:
            Formatter.format(format_str, 'eggs')
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_formatter_6(self):
        format_str = 'milk and {:.>10}'
        self.assertEqual(Formatter.format(format_str, 'eggs'), 'milk and ......eggs')

    def test_formatter_7(self):
        format_str = 'milk and {:.>{}}'
        self.assertEqual(Formatter.format(format_str, 'eggs', 10), 'milk and ......eggs')

    def test_formatter_8(self):
        format_str = 'milk and {:{}{}{}}'
        self.assertEqual(Formatter.format(format_str, 'eggs', '.', '>', 10), 'milk and ......eggs')

    def test_formatter_9(self):
        format_str = 'milk and {2:{bob}{0}{0}}'
        try:
            self.assertEqual(Formatter.format(format_str, 'eggs', '.', '>', 10), 'milk and ......eggs')
        except KeyError:
            pass
        else:
            raise AssertionError

    def test_formatter_10(self):
        format_str = 'milk and {2:{bob}{0}{1}}'
        self.assertEqual(Formatter.format(format_str, '>', 10, 'eggs', bob='.'), 'milk and ......eggs')

    def test_formatter_11(self):
        format_str = "First, thou shalt count to {0}"
        self.assertEqual(Formatter.format(format_str, 0x54), 'First, thou shalt count to 84')

    def test_formatter_12(self):
        Weighted = namedtuple('Weighted', 'weight')
        format_str = "Weight in tons {0.weight}"
        self.assertEqual(Formatter.format(format_str, Weighted(5)), "Weight in tons 5")

    def test_formatter_13(self):
        format_str = "Units destroyed: {players[0]}"
        self.assertEqual(Formatter.format(format_str, players=[1,2,3,4]), "Units destroyed: 1")

    def test_formatter_14(self):
        Weighted = namedtuple('Weighted', 'weight')
        format_str = "Bring out the {name!r}"
        self.assertEqual(Formatter.format(format_str, name=Weighted(5)), "Bring out the Weighted(weight=5)")


