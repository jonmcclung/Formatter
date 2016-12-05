from ..utils import EqualityByValue


@EqualityByValue
class Token:
    def __init__(self, value, token_type):
        self.value = value
        self.token_type = token_type
        assert token_type is not None

    def __str__(self):
        return str(self.value)
