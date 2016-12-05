import unittest
from unittest import TestCase

from ..core.Lexer import Lexer
from ..core.Parser import Parser, ParserException
from ..core.Scanner import Scanner

from ..core.Node import Literal, Replacement, FieldName, FormatString, Index, FormatSpec, Conversion


class ParserTest(TestCase):
    def get_tokens(self, text):
        lexer = Lexer(text)
        return list(token for token in lexer)

    def test_basic_0(self):
        parser = Parser(Scanner(self.get_tokens('abc')))
        parser.parse()
        self.assertEqual(parser.format_string, FormatString([Literal('abc')]))

    def test_basic_1(self):
        parser = Parser(Scanner(self.get_tokens('a{{board oairent05_c}}{{')))
        parser.parse()
        self.assertEqual(parser.format_string, FormatString([Literal('a{{board oairent05_c}}{{')]))
        self.assertEqual(parser.format_string.nodes[0].text, 'a{board oairent05_c}{')

    def test_basic_2(self):
        parser = Parser(Scanner(self.get_tokens('{}')))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString([Replacement(FieldName(0))]))

    def test_basic_3(self):
        parser = Parser(Scanner(self.get_tokens('{a}')))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString([Replacement(field_name=FieldName('a'))]))

    def test_basic_4(self):
        parser = Parser(Scanner(self.get_tokens('abracadabra    \n\\n{a}')))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString([Literal('abracadabra    \n\\n'), Replacement(field_name=FieldName('a'))]))

    def  test_basic_5(self):
        parser = Parser(Scanner(self.get_tokens('{{ aroe}} {{ {abrac[2][42][4]}}}')))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString(
                [Literal('{{ aroe}} {{ '), Replacement(field_name=FieldName('abrac', [Index(2), Index(42), Index(4)])),
                 Literal('}}')]))

    def test_switching_fails_0(self):
        parser = Parser(Scanner(self.get_tokens('{} {1}')))
        try:
            parser.parse()
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_switching_fails_1(self):
        parser = Parser(Scanner(self.get_tokens('{123} {} {} {bob}')))
        try:
            parser.parse()
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_long_automatic(self):
        parser = Parser(Scanner(self.get_tokens('{} {abby} merry {} seion  ]]{bob}')))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString(
                [Replacement(FieldName(0)), Literal(' '), Replacement(field_name=FieldName('abby')), Literal(' merry '),
                 Replacement(FieldName(1)), Literal(' seion  ]]'), Replacement(field_name=FieldName('bob'))]))

    def test_automatic_replacement_with_brackets(self):
        parser = Parser(Scanner(self.get_tokens('{[]}')))
        try:
            parser.parse()
        except ParserException:
            pass
        else:
            raise AssertionError

    def test_automatic_replacement_with_period(self):
        parser = Parser(Scanner(self.get_tokens('{.}')))
        try:
            parser.parse()
        except ParserException:
            pass
        else:
            raise AssertionError

    def test_format_spec_0(self):
        format_spec = FormatSpec()
        self.assertEqual(format_spec.format([1, 2, 3]), '[1, 2, 3]')

    def test_format_spec_1(self):
        replacement = Replacement(FieldName(0), Conversion('s'), FormatSpec('>12'))
        self.assertEqual(replacement.eval([1, 2, 3]), '   [1, 2, 3]')

    def test_nested_0(self):
        format_str = 'milk and {:.>{}}'
        parser = Parser(Scanner(self.get_tokens(format_str)))
        parser.parse()
        self.assertEqual(
            parser.format_string,
            FormatString(
                [Literal('milk and '),
                 Replacement(FieldName(0), None, FormatSpec('.>{}', [Replacement(FieldName(1))]))]))

if __name__ == '__main__':
    unittest.main()