# because of circular import
from symbol_table import SymbolTable


class Errors:
    class InvalidCharacterError(Exception):
        """If there're Token sequences generated from the input that are not
        permitted by the grammar rules"""
        def __init__(self, found, found_pos):
            self.description = f"InvalidCharacterError: '{found}' is not a "\
                "permitted character"
            super().__init__(self.description)
            self.expected = None
            self.found = found
            self.found_pos = found_pos

    class UnclosedCharacterError(Exception):
        """If a character has a opening apostrophe but not a closing one"""
        def __init__(self, expected, found, found_pos):
            self.description = f"UnclosedCharacterError: Expected {expected},"\
                f" found {found}"
            super().__init__(self.description)
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class NoApplicableRuleError(Exception):
        """If no rule is applicable in a situation where several undistinguishable
        alternatives are possible"""
        def __init__(self, expected, found, found_pos):
            self.description = f"NoApplicableRuleError: Expected '{expected}'"\
                f", found '{found}'"
            super().__init__(self.description)
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class MismatchedTokenError(Exception):
        """If Token shouldn't syntactically appear at this position"""
        def __init__(self, expected, found, found_pos):
            self.description = f"MismatchedTokenError: Expected '{expected}'"\
                f", found '{found}'"
            super().__init__(self.description)
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class TastingError(Exception):
        """This error can only appear while tasting and should be raised if a
        Token appears that can only be part of the other tasting choice"""
        def __init__(self, ):
            super().__init__("This error should never be visible")

    class UnknownIdentifierError(Exception):
        """If Token shouldn't syntactically appear at this position"""
        def __init__(self, identifier, identifier_pos):
            self.description = "UnknownIdentifierError: Identifier "\
                f"'{identifier}' wasn't declared yet."
            super().__init__(self.description)
            self.expected = None
            self.expected_pos = None
            self.found = identifier
            self.found_pos = identifier_pos

    class TooLargeLiteralError(Exception):
        """If theu literal assigned to a variable is too large for the datatype of
        the variable"""
        def __init__(self, identifier, assignment, assignment_pos):
            dtype = SymbolTable().resolve(identifier).datatype
            self.description = f"TooLargeLiteralError: Literal {assignment} "\
                f"assigned to variable {identifier} of type {dtype} is too large"
            super().__init__(self.description)
            self.expected = None
            self.expected_pos = None
            self.found = assignment
            self.found_pos = assignment_pos

    class NoMainFunctionError(Exception):
        """If there's no main function within the given file"""
        def __init__(self, fname):
            self.description = "NoMainFunctionError: There's no main function"\
                f" in file {fname}"
            super().__init__(self.description)
            self.expected = None
            self.expected_pos = None
            self.found = None
            self.found_pos = None
