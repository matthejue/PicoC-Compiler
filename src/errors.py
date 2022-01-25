class Errors:
    class InvalidCharacterError(Exception):
        """If there're Token sequences generated from the input that are not
        permitted by the grammar rules"""
        def __init__(self, found, found_pos):
            self.description = f"InvalidCharacterError: '{found}' is not a "\
                "permitted character"
            self.found = found
            self.found_pos = found_pos

    class UnclosedCharacterError(Exception):
        """If a character has a opening apostrophe but not a closing one"""
        def __init__(self, expected, found, found_pos):
            self.description = f"UnclosedCharacterError: Expected {expected},"\
                f" found {found}"
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class NoApplicableRuleError(Exception):
        """If no rule is applicable in a situation where several undistinguishable
        alternatives are possible"""
        def __init__(self, expected, found, found_pos):
            self.description = f"NoApplicableRuleError: Expected '{expected}'"\
                f", found '{found}'"
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class MismatchedTokenError(Exception):
        """If Token shouldn't syntactically appear at this position"""
        def __init__(self, expected, found, found_pos):
            # there can be several expected and these already have single quotes
            self.description = f"MismatchedTokenError: Expected '{expected}'"\
                f", found '{found}'"
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class TastingError(Exception):
        """This error can only appear while tasting and should be raised if a
        Token appears that can only be part of the other tasting choice"""
        def __init__(self, ):
            self.description = "This error should never be visible"

    class UnknownIdentifierError(Exception):
        """If Token shouldn't syntactically appear at this position"""
        def __init__(self, found, found_pos):
            self.description = "UnknownIdentifierError: Identifier "\
                f"'{found}' wasn't declared yet"
            self.found = found
            self.found_pos = found_pos

    class TooLargeLiteralError(Exception):
        """If the literal assigned to a variable is too large for the datatype of
        the variable"""
        def __init__(self, found, found_pos, found_symbol_type, found_from,
                     found_to):
            self.description = f"TooLargeLiteralError: Literal '{found}' is too large"
            self.found = found
            self.found_pos = found_pos
            self.found_symbol_type = found_symbol_type
            self.found_from = found_from
            self.found_to = found_to

    class RedefinitionError(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = f"RedefinitionError: Redefinition of '{found}'"
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class ConstReassignmentError(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = "ConstReassignmentError: Can't reassign a new "\
            f"value to named constant '{found}'"
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class NoMainFunctionError(Exception):
        """If there's no main function within the given file"""
        def __init__(self, fname):
            self.description = "NoMainFunctionError: There's no main function"\
                f" in file '{fname}'"

    class NotImplementedYetError(Exception):
        """Feature that isn't implemented yet"""
        def __init__(self, feature_description):
            self.description = "NotImplementedYet: The feature of using "\
                f"{feature_description} is not implemented yet"
