class SyntaxError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammer rules"""

    def __init__(self, expected, found):
        self.description = "SyntaxError: Expected " + "expected" + ", found " \
            + found
        super().__init__(self.description)


class InvalidCharacterError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammer rules"""

    def __init__(self, found):
        self.description = "InvalidCharacterError: " + \
            str(found) + " is not a permitted character"
        super().__init__(self.description)
