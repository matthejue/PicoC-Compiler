# because of circular import
import lexer


class InvalidCharacterError(Exception):
    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""
    def __init__(self, value, position):
        self.description = f"InvalidCharacterError: "\
            f"'{value}' is not a permitted character"
        super().__init__(self.description)
        self.expected = None
        self.found = lexer.Token(None, value=value, position=position)


class UnclosedCharacterError(Exception):
    """If a character has a opening apostrophe but not a closing one"""
    def __init__(self, expected, value, position):
        self.description = f"UnclosedCharacterError: Expected {expected},"\
            f" found {value}"
        super().__init__(self.description)
        self.expected = expected
        self.found = lexer.Token(None, value=value, position=position)


class NoApplicableRuleError(Exception):
    """If no rule is applicable in a situation where several undistinguishable
    alternatives are possible"""
    def __init__(self, expected, found):
        self.description = f"NoApplicableRuleError: Expected '{expected}'"\
            f", found '{found.value}'"
        super().__init__(self.description)
        self.expected = expected
        self.found = found


class MismatchedTokenError(Exception):
    """If Token shouldn't syntactically appear at this position"""
    def __init__(self, expected, found):
        self.description = f"MismatchedTokenError: Expected '{expected}'"\
            f", found '{found.value}'"
        super().__init__(self.description)
        self.expected = expected
        self.found = found


class UnknownIdentifierError(Exception):
    """If Token shouldn't syntactically appear at this position"""
    def __init__(self, found):
        self.description = f"UnknownIdentifierError: Identifier "\
            f"'{found.value}' wasn't declared yet."
        super().__init__(self.description)
        self.found = found
