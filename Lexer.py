from string import digits, whitespace, punctuation, printable, octdigits, hexdigits

from Node import Replacement, Conversion, FormatSpec, Attribute, Index
from Scanner import Scanner
from Token import Token
from TokenEnum import TokenEnum


class LexerException(Exception):
    pass


class Lexer:
    delimiter = set('{}')
    punctuation = set(punctuation) - delimiter - set('_')
    literal = set(printable) - delimiter
    integer = set(digits)
    id_ = set(printable) - (punctuation | delimiter | set(whitespace))
    id_start = id_ - integer

    @staticmethod
    def get_type(char):
        types = [(Lexer.id_start, TokenEnum.id),
                 (Lexer.integer, TokenEnum.integer),
                 (Lexer.punctuation, TokenEnum.punctuation),
                 (Lexer.delimiter, TokenEnum.delimiter)]
        for char_set, token_type in types:
            if char in char_set:
                return token_type

    @staticmethod
    def make_token(string):
        return Token(string, Lexer.get_type(string[0]))

    @staticmethod
    def expect(condition, msg):
        if not condition:
            raise LexerException(msg)

    def __init__(self, pattern: str):
        self.scanner = Scanner(pattern)
        assert self.scanner.index == 0

    def get_literal(self):
        i = 0
        while True:
            while self.scanner.peek(i) in Lexer.literal:
                i += 1
            curr = self.scanner.peek(i)
            if curr is None:
                return self.scanner.collect(i)
            elif self.scanner.peek(i + 1) == curr:  # escaped brace
                i += 2
            else:
                self.expect(curr != '}', "unmatched '}'")
                return self.scanner.collect(i)

    def lex_binary(self):
        """
        assumes that self.scanner.peek() == '0'
        """
        if self.scanner.peek(1) not in 'Bb':
            return None
        self.scanner.consume(2)
        return int(self.scanner.get_while(lambda char: char in '01'), 2)

    def lex_octal(self):
        """
        assumes that self.scanner.peek() == '0'
        """
        if self.scanner.peek(1) not in 'Oo':
            return None
        self.scanner.consume(2)
        return int(self.scanner.get_while(lambda char: char in octdigits), 8)

    def lex_hex(self):
        """
        assumes that self.scanner.peek() == '0'
        """
        if self.scanner.peek(1) not in 'Xx':
            return None
        self.scanner.consume(2)
        return int(self.scanner.get_while(lambda char: char in hexdigits), 16)

    def lex_int(self):
        if self.scanner.peek() == '0':
            for type, method in zip(
                    ['binary', 'octal', 'hexadecimal'],
                    [self.lex_binary, self.lex_octal, self.lex_hex]):
                number = method()
                if number:
                    return Token(number, TokenEnum.integer)
                elif number == '':
                    raise LexerException('expected {} string'.format(type))
            else:
                zeroes = self.scanner.get_while(lambda char: char == '0')
                Lexer.expect(self.scanner.peek() not in digits, 'invalid integer')
                return Token(0, TokenEnum.integer)
        elif self.scanner.peek() in digits:
            return Token(int(self.scanner.get_while(lambda char: char in digits)), TokenEnum.integer)
        else:
            return None

    def lex_replacement(self):
        """
        yields children for all parts of the replacement and the closing brace,
        and then leaves the scanner in a state where scanner.peek() is the first
        character after the closing brace
        """
        """
        replacement_field::=  "{"[field_name]["!"conversion][":" format_spec]"}"
        field_name::=  arg_name("."attribute_name | "["element_index"]") *
        arg_name::=  [identifier | integer]
        attribute_name::=  identifier
        element_index::=  integer | index_string
        index_string::= < any source character except "]" > +
        conversion::=  "right" | "s" | "a"
        format_spec::= < described in the next section >
        """
        """
        format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
        fill        ::=  <any character>
        align       ::=  "<" | ">" | "=" | "^"
        sign        ::=  "+" | "-" | " "
        width       ::=  integer
        precision   ::=  integer
        type        ::=  "board" | "c" | "down" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"
        """
        if self.scanner:
            self.expect(self.scanner.consume() == '{', "unmatched '{'")
            yield Replacement.l_brace
            curr = self.scanner.consume()
            while curr:
                if curr == '[':
                    yield Index.l_bracket
                    if self.scanner.peek() == ']':
                        self.scanner.consume()
                        yield Index.r_bracket
                    else:
                        num_index = self.lex_int()
                        if num_index:
                            yield num_index
                        else:
                            yield Token(
                                self.scanner.get_while(lambda char: char != ']'),
                                TokenEnum.literal)
                        Lexer.expect(self.scanner.consume() == ']', "unmatched ']'")
                        yield Index.r_bracket
                elif curr == '.':
                    yield Attribute.period
                elif curr == '!':
                    yield Conversion.exclamation
                elif curr == ':':
                    yield FormatSpec.colon
                elif curr == '}':
                    yield Replacement.r_brace
                    return
                elif curr == '{':
                    self.scanner.backup()
                    for token in self.lex_replacement():
                        yield token
                elif curr in digits:
                    self.scanner.backup()
                    yield self.lex_int()
                elif curr in Lexer.id_start:
                    yield Lexer.make_token(self.scanner.get_while(lambda char: char in Lexer.id_, 1))
                else:
                    yield Lexer.make_token(curr)
                curr = self.scanner.consume()
            raise LexerException("unmatched '{'")

    def lex(self):
        while self.scanner:
            literal = self.get_literal()
            if literal:
                yield Token(literal, TokenEnum.literal)
            for token in self.lex_replacement():
                yield token

    def __iter__(self):
        for token in self.lex():
            yield token

    @property
    def tokens(self):
        assert self.scanner.index == 0
        return Scanner(list(self.lex()))
