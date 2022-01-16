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
            # there can be several expected and these already have single quotes
            self.description = f"MismatchedTokenError: Expected {expected}"\
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
        def __init__(self, found, found_pos):
            self.description = "UnknownIdentifierError: Identifier "\
                f"'{found}' wasn't declared yet"
            super().__init__(self.description)
            self.found = found
            self.found_pos = found_pos

    class TooLargeLiteralError(Exception):
        """If theu literal assigned to a variable is too large for the datatype of
        the variable"""
        def __init__(self, variable, variable_pos, variable_type, assignment,
                     assignment_pos):
            self.description = f"TooLargeLiteralError: Literal {assignment} "\
                f"assigned to variable {variable} of type {variable_type} is too large"
            super().__init__(self.description)
            self.variable = variable
            self.variable_pos = variable_pos
            self.variable_type = variable_type
            self.found = assignment
            self.found_pos = assignment_pos

    class RedefinitionError(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = f"RedefinitionError: Redefinition of {found}"
            super().__init__(self.description)
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class NoMainFunctionError(Exception):
        """If there's no main function within the given file"""
        def __init__(self, fname):
            self.description = "NoMainFunctionError: There's no main function"\
                f" in file {fname}"
            super().__init__(self.description)

    class NotImplementedYetError(Exception):
        """Feature that isn't implemented yet"""
        def __init__(self, feature_description):
            self.description = "NotImplementedYet: The feature of using "\
                f"{feature_description} is not implemented yet"
            super().__init__(self.description)
