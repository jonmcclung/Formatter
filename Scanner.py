from typing import Sequence, TypeVar, Callable

T = TypeVar('T')


class Scanner(Sequence[T]):
    def __init__(self, tokens: Sequence[T]):
        self.tokens = tokens
        self.index = 0

    def peek(self, skip=0) -> T:
        """
        returns the next token that will be read or None if we are at
        the end of the input stream.
        Optional parameter skip specifies how many children ahead to look.
        """
        try:
            return self.tokens[self.index + skip]
        except IndexError:
            return None

    def __bool__(self):
        return self.index < len(self.tokens)

    def backup(self, tokens=1):
        """
        backs up token stream by tokens. Throws an IndexError if
        you back up to before the start of the stream
        """
        self.index -= tokens
        if self.index < 0:
            raise IndexError('cannot backup to before start of tokens')

    def consume(self, tokens=1) -> T:
        """
        moves up by children children and returns the token there after
        incrementing self.index
        children must be > 0
        If you consume exactly as many children as there are + 1,
        you will get None back. If you consume more than that, you will get
         an IndexError
        """
        self.index += tokens
        if self.index <= len(self.tokens) + 1:
            return self.peek(-1)
        raise IndexError('attempted to read ' + str(self.index - len(self.tokens)) + ' children too many')

    def collect(self, length, backtrack=0, lookahead=0) -> Sequence[T]:
        """
        length must be >= 0
        """
        assert length >= 0
        res = self.tokens[self.index - backtrack:self.index + length + lookahead]
        self.index += length
        return res

    def get_while(self, condition: Callable[[T], bool], prev_offset=0, next_offset=0) -> Sequence[T]:
        """
        returns self.tokens starting from the initial index - prev_offset
        until and including the last index that met the condition + next_offset.
        If the token at the current index does not meet condition,
        it will simply return self.tokens[self.index - prev_offset:self.index + next_offset].
        after this method, self.index points to the first token that did not meet condition
        """
        initial = self.index
        while self.peek() and condition(self.peek()):
            self.index += 1

        return self.tokens[initial - prev_offset:self.index + next_offset]

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        return self.tokens.__iter__
