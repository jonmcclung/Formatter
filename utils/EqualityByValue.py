def EqualityByValue(cls):
    class Wrapper(cls):
        def __eq__(self, other):
            if isinstance(other, cls):
                return self.__dict__ == other.__dict__
            return NotImplemented

        def __ne__(self, other):
            if isinstance(other, cls):
                return not self.__eq__(other)
            return NotImplemented

        def __hash__(self):
            return hash(tuple(sorted(self.__dict__.items())))

        def __repr__(self):
            values = ', '.join(
                ''.join([str(attribute), ': ', str(value)])
                        for attribute, value in
                        self.__dict__.items())
            return '<{}({})>'.format(cls.__name__, values)
    return Wrapper