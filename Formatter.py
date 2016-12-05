from Lexer import Lexer
from Parser import Parser


class Formatter:
    @staticmethod
    def format(format_str, *args, **kwargs):
        lexer = Lexer(format_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        parser.parse()
        format_string = parser.format_string
        return format_string.format(*args, **kwargs)