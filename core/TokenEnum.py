from enum import unique, Enum


@unique
class TokenEnum(Enum):
    literal = 0
    id = 1
    punctuation = 2
    integer = 3
    delimiter = 4