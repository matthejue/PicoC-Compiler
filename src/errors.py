from colormanager import ColorManager as CM
from lark import Token
from dataclasses import dataclass


@dataclass
class Pos:
    line: int
    column: int

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column


@dataclass
class Range:
    start_pos: Pos
    end_pos: Pos


class Errors:
    class UnexpectedCharacterError(Exception):
        def __init__(self, expected: str, found: str, found_pos: Pos):
            self.description = (
                f"{CM().YELLOW}UnexpectedCharacter{CM().RESET}: No terminal "
                f"matches '{found}' in the current lexical context of "
                f"{expected}"
            )
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class UnexpectedTokenError(Exception):
        def __init__(self, expected: str, found: Token, found_range: Range):
            self.description = (
                f"{CM().YELLOW}UnexpectedToken{CM().RESET}: Expected e.g. {expected}"
                f", found '{found}'"
            )
            self.expected = expected
            self.found = found
            self.found_range = found_range

    class UnknownIdentifierError(Exception):
        """If Token shouldn't syntactically appear at this position"""

        def __init__(self, found, found_pos):
            self.description = (
                f"{CM().YELLOW}UnknownIdentifierError{CM().RESET}: Identifier "
                f"'{found}' wasn't declared yet"
            )
            self.found = found
            self.found_pos = found_pos

    class TooLargeLiteralError(Exception):
        """If the literal assigned to a variable is too large for the datatype of
        the variable"""

        def __init__(self, found, found_pos, found_symbol_type, found_from, found_to):
            self.description = f"{CM().YELLOW}TooLargeLiteralError{CM().RESET}: Literal '{found}' is too large"
            self.found = found
            self.found_pos = found_pos
            self.found_symbol_type = found_symbol_type
            self.found_from = found_from
            self.found_to = found_to

    class RedefinitionError(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = (
                f"{CM().YELLOW}RedefinitionError{CM().RESET}: Redefinition of '{found}'"
            )
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class ConstReassignmentError(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = (
                f"{CM().YELLOW}ConstReassignmentError{CM().RESET}: Can't reassign a new "
                f"value to named constant '{found}'"
            )
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class NoMainFunctionError(Exception):
        """If there's no main function within the given file"""

        def __init__(self, fname):
            self.description = (
                f"{CM().YELLOW}NoMainFunctionError{CM().RESET}: There's no main function"
                f" in file '{fname}'"
            )

    class MoreThanOneMainFunctionError(Exception):
        def __init__(self, first_pos, second_pos):
            self.description = (
                f"{CM().YELLOW}MoreThanOneMainFunctionError{CM().RESET}: There're at "
                "least two main functions"
            )
            self.first_pos = first_pos
            self.second_pos = second_pos

    class NotImplementedYetError(Exception):
        """Feature that isn't implemented yet"""

        def __init__(self, feature_description):
            self.description = (
                f"{CM().YELLOW}NotImplementedYet{CM().RESET}: The feature of using "
                f"{feature_description} is not implemented yet"
            )
