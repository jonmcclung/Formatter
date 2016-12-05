from TokenEnum import TokenEnum
from Node import Replacement, Literal, Conversion, FormatSpec, FieldName, FormatString, Attribute, Index, Align, Sign
from Scanner import Scanner
from Token import Token


class ParserException(Exception):
    pass


class Parser:
    def __init__(self, tokens: Scanner[Token]):
        self.tokens = tokens
        self.format_string = FormatString()
        # None means undecided
        self.automatic = None
        self.automatic_index = -1

    @staticmethod
    def expect(condition, msg):
        if not condition:
            raise ParserException(msg)

    def consume_value(self, tokens=0):
        return self.tokens.consume(tokens).value

    def parse(self):
        while self.tokens:
            literal = self.parse_literal()
            if literal:  # is not None
                self.format_string.append(literal)
            else:
                replacement = self.parse_replacement()
                if replacement:
                    self.format_string.append(replacement)
                else:
                    raise ParserException('expected a literal or a \'{\'')
        return self.format_string

    def parse_literal(self):
        token = self.tokens.consume()
        if token.token_type == TokenEnum.literal:
            return Literal(token.value)
        self.tokens.backup()
        return None

    def parse_replacement(self):
        # "{" [field_name] ["!" conversion] [":" format_spec] "}"
        if self.tokens.peek() != Replacement.hint:
            return None
        self.tokens.index += 1
        res = Replacement(
            self.parse_field_name(),
            self.parse_conversion(),
            self.parse_format_spec())
        self.expect(self.tokens.consume() == Replacement.r_brace, "unmatched '{'")
        return res

    def parse_field_name(self):
        if self.tokens.peek() in [Conversion.hint, FormatSpec.hint, Replacement.end]:
            if self.automatic is None:
                self.automatic = True
            if self.automatic:
                self.automatic_index += 1
                return FieldName(self.automatic_index)
            else:
                raise ValueError('cannot switch from manual field numbering to automatic field specification')

        argument = self.tokens.consume()

        if argument.token_type == TokenEnum.integer:
            if self.automatic:
                raise ValueError('cannot switch from automatic field numbering to automatic field specification')
            elif self.automatic is None:
                self.automatic = False
        else:
            Parser.expect(argument.token_type == TokenEnum.id,
                          'expected an identifier, but got {}'.format(argument.value))

        getters = []
        while True:
            if str(self.tokens.peek()) in '!:}':
                break
            else:
                Parser.expect(
                    self.parse_index(getters) or self.parse_attribute(getters),
                    str(self.tokens.peek()) + ' is not a valid token in this context. ' +
                    'Expected one of !, :, }, [, .')

        return FieldName(argument.value, getters)

    def parse_conversion(self):
        if self.tokens.peek() != Conversion.hint:
            return None
        char = self.consume_value(2)
        Parser.expect(char in Conversion.valid_chars, 'expected conversion ({!r}) to be one of r, s, a'.format(char))
        return Conversion(char)

    def true_if_has(self, char):
        if self.tokens.peek().value == char:
            self.tokens.consume()
            return True
        else:
            return False

    def parse_format_spec(self):
        if self.tokens.peek() != FormatSpec.hint:
            return None

        token = self.tokens.consume(2)
        format_str = []
        inners = []
        while token:
            if token == Replacement.l_brace:
                self.tokens.backup()
                inners.append(self.parse_replacement())
                format_str.append('{}')
            elif token == Replacement.r_brace:
                self.tokens.backup()
                return FormatSpec(''.join(format_str), inners)
            else:
                format_str.append(str(token.value))
            token = self.tokens.consume()
        assert False, "Lexer missed unmatched '{'"

    '''
    if self.tokens.peek() in Align.valid_tokens:
        align = self.consume_value()
    elif self.tokens.peek(1) in Align.valid_tokens:
        fill = self.consume_value()
        align = self.consume_value()
    if self.tokens.peek() in Sign.valid_tokens:
        sign = self.consume_value()
    hash_ = self.true_if_has('#')
    zero_pad = self.true_if_has('0')
    if self.tokens.peek().token_type == TokenEnum.integer:
        width = self.consume_value()
    else:
        width = 0
    comma = self.true_if_has(',')
    if self.true_if_has('.'):
        precision = self.consume_value()
        Parser.expect(type(precision) == int, 'expected an integer precision following that period')
    if self.tokens.peek() in Type_:
        type_ = self.consume_value())
    '''

    def parse_index(self, getters):
        if self.tokens.peek() != Index.l_bracket:
            return False
        index = self.tokens.consume(2)
        Parser.expect(self.tokens.consume() == Index.r_bracket, "improperly matched '['")
        getters.append(Index(index.value))
        return True

    def parse_attribute(self, getters):
        if self.tokens.peek() != Attribute.period:
            return False
        attribute = self.tokens.consume(2)
        Parser.expect(attribute.token_type == TokenEnum.id, 'expected an id following that period')
        getters.append(Attribute(attribute.value))
        return True
