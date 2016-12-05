from typing import Sequence, Union

from .Token import Token

from ..utils import EqualityByValue
from .TokenEnum import TokenEnum


@EqualityByValue
class Node:
    pass


@EqualityByValue
class FormatString(Node):
    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def append(self, node: Node):
        self.nodes.append(node)

    def format(self, *args, **kwargs):
        return ''.join(
            node.eval(*args, **kwargs)
            for node in self.nodes)


@EqualityByValue
class Replacement(Node):
    l_brace = Token('{', TokenEnum.delimiter)
    r_brace = Token('}', TokenEnum.delimiter)

    hint = l_brace
    end = r_brace

    def __init__(self, field_name, conversion=None, format_spec=None):
        self.field_name = field_name
        self.conversion = conversion or Conversion()
        self.format_spec = format_spec or FormatSpec()

    def eval(self, *args, **kwargs):
        return self.format_spec.format(self.conversion.eval(self.field_name.eval(*args, **kwargs)), *args, **kwargs)


@EqualityByValue
class Getter(Node):
    def get(self, arg):
        pass


@EqualityByValue
class Attribute(Getter):
    period = Token('.', TokenEnum.punctuation)

    def __init__(self, attr):
        self.attr = attr

    def get(self, arg):
        return getattr(arg, self.attr)


@EqualityByValue
class Index(Getter):
    l_bracket = Token('[', TokenEnum.punctuation)
    r_bracket = Token(']', TokenEnum.punctuation)

    def __init__(self, index):
        self.index = index

    def get(self, arg):
        return arg[self.index]


@EqualityByValue
class FieldName(Node):
    def __init__(self, argument: Union[int, str], getters: Sequence[Getter] = None):
        self.argument = argument
        self.getters = getters or []

    def eval(self, *args, **kwargs):
        if type(self.argument) == int:
            value = args[self.argument]
        else:
            value = kwargs[self.argument]

        for getter in self.getters:
            value = getter.get(value)

        return value


@EqualityByValue
class Conversion(Node):
    exclamation = Token('!', TokenEnum.punctuation)
    hint = exclamation

    valid_chars = {'r': repr, 's': str, 'a': ascii, '': lambda string: string}

    def __init__(self, char=''):
        self.eval = Conversion.valid_chars[char]


@EqualityByValue
class Sign:
    plus = Token('+', TokenEnum.punctuation)
    minus = Token('-', TokenEnum.punctuation)
    space = Token(' ', TokenEnum.punctuation)
    valid_tokens = [plus, minus, space]


@EqualityByValue
class Align:
    def left(self, string):
        return string + self.fill * (self.width - len(string))

    def center(self, string):
        return self.fill * ((self.width - len(string)) // 2) + string + self.fill * ((self.width - len(string)) // 2)

    def right(self, string):
        return self.fill * (self.width - len(string)) + string

    def sign(self, string):
        return self.sign + self.right(string)

    valid_tokens = {Token('<', TokenEnum.punctuation): left,
                    Token('^', TokenEnum.punctuation): center,
                    Token('>', TokenEnum.punctuation): right,
                    Token('=', TokenEnum.punctuation): sign}

    def __init__(self, is_number, fill=' ', char=None, sign=None, width=0):
        self.fill = fill
        self.is_number = is_number
        self.sign = sign
        self.width = width
        if char is None:
            self.align = self.right if is_number else self.left
        self.align = self.valid_tokens[char]
        if self.align == self.sign and not is_number:
            raise ValueError('only numbers may be aligned with \'=\'')


@EqualityByValue
class Type:
    default = ''
    string = 's'
    string_default = string
    binary = 'board'
    character = 'c'
    decimal = 'down'
    octal = 'o'
    lower_hex = 'x'
    upper_hex = 'X'
    number = 'n'
    number_default = decimal
    lower_exponent = 'e'
    upper_exponent = 'E'
    lower_fixed_point = 'f'
    upper_fixed_point = 'F'
    lower_general = 'g'
    upper_general = 'G'
    percent = '%'
    float_default = ''


@EqualityByValue
class FormatSpec(Node):
    colon = Token(':', TokenEnum.punctuation)
    hint = colon

    def format(self, string, *args, **kwargs):
        for inner in self.inners:
            self.format_str = self.format_str.replace('{}', inner.eval(*args, **kwargs), 1)
        return string.__format__(self.format_str)

    def __init__(self, format_str: str='', inners=None):
        self.format_str = format_str
        self.inners = inners or []

'''
    def __init__(self, is_number, is_float, align, sign, hash_, zero_pad, width, comma, precision, type_):
        self.is_number = is_number or is_float
        self._is_float = is_float
        self.align = Align(' ', is_number)
        if is_number:
            self.sign = Sign.minus
            self.hash_ = False
            self.zero_pad = False
        else:
            self.align = Align.left
        self.width = 0
        if is_number:
            self.comma = False
            if is_float:
                self.period = False
                self.precision = None
                self.type_ = Type.float_default
            else:
                self.type_ = Type.number_default
        else:
            self.type_ = Type.string_default

    @property
    def is_float(self):
        return self._is_float

    @is_float.setter
    def is_float(self, is_float):
        self.is_number = self.is_number or is_float
        self._is_float = is_float

    @property
    def sign(self):
        return self.sign

    @sign.setter
    def sign(self, sign):
        if not self.is_number:
            raise ValueError('This is not a number, may not set sign')
        self.sign = sign

    @property
    def hash_(self):
        return self.hash_

    @hash_.setter
    def hash_(self, hash):
        if not self.is_number:
            raise ValueError('This is not a number, may not set hash')
        self.hash_ = hash

    @property
    def zero_pad(self):
        return self.zero_pad

    @zero_pad.setter
    def zero_pad(self, zero_pad):
        if not self.is_number:
            raise ValueError('This is not a number, may not set zero padding')
        self.zero_pad = zero_pad

    @property
    def comma(self):
        return self.comma

    @comma.setter
    def comma(self, comma):
        if not self.is_number:
            raise ValueError('This is not a number, may not set comma')
        self.comma = comma
'''

@EqualityByValue
class Literal(Node):
    def __init__(self, text):
        formatted_text = []
        i = 0
        while i < len(text):
            formatted_text.append(text[i])
            if text[i] in '{}':
                i += 2
            else:
                i += 1
        self.text = ''.join(formatted_text)

    def eval(self, *args, **kwargs):
        return self.text
