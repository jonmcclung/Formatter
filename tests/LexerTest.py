import unittest
from string import digits

from Lexer import Lexer
from Scanner import Scanner
from TokenEnum import TokenEnum
from Node import FieldName, Index, Replacement, FormatSpec
from Token import Token


class LexerTest(unittest.TestCase):

    def get_tokens(self, text):
        lexer = Lexer(text)
        return list(token for token in lexer)

    def test_scanner_get_while(self):
        scanner = Scanner('42')
        self.assertEqual(
            scanner.get_while(lambda char: char in digits),
            '42')
        self.assertEqual(scanner.peek(), None)

    def test_basic_0(self):
        self.assertEqual(self.get_tokens('abc'), [Token('abc', TokenEnum.literal)])

    def test_basic_1(self):
        self.assertEqual(self.get_tokens('a{{board oairent05_c}}{{'), [Token('a{{board oairent05_c}}{{', TokenEnum.literal)])

    def test_basic_replacement_0(self):
        self.assertEqual(self.get_tokens('{}'), [Token('{', TokenEnum.delimiter), Token('}', TokenEnum.delimiter)])

    def test_basic_replacement_1(self):
        self.assertEqual(
            self.get_tokens('{a}'),
            [Token('{', TokenEnum.delimiter), Token('a', TokenEnum.id), Token('}', TokenEnum.delimiter)])

    def test_basic_replacement_2(self):
        self.assertEqual(
            self.get_tokens('abracadabra    \n\\n{a}'),
            [Token('abracadabra    \n\\n', TokenEnum.literal), Token('{', TokenEnum.delimiter),
             Token('a', TokenEnum.id), Token('}', TokenEnum.delimiter)])

    def test_basic_replacement_3(self):
        self.maxDiff = None
        self.assertEqual(
            self.get_tokens('{{ aroe}} {{ {abrac[]42[4]}}}'),
            [Token('{{ aroe}} {{ ', TokenEnum.literal), Token('{', TokenEnum.delimiter),
             Token('abrac', TokenEnum.id),
             Index.l_bracket, Index.r_bracket,
             Token(42, TokenEnum.integer), Index.l_bracket,
             Token(4, TokenEnum.integer), Index.r_bracket,
             Token('}', TokenEnum.delimiter), Token('}}', TokenEnum.literal)])

    def test_0(self):
        self.assertEqual(
            self.get_tokens('milk and {:.>{}}'),
            [Token('milk and ', TokenEnum.literal), Replacement.l_brace, FormatSpec.colon,
             Token('.', TokenEnum.punctuation), Token('>', TokenEnum.punctuation),
             Replacement.l_brace, Replacement.r_brace, Replacement.r_brace])
