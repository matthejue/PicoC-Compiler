from colormanager import ColorManager as CM
from lark.lexer import Token
from global_classes import Pos


class Errors:
    class UnexpectedCharacter(Exception):
        def __init__(self, expected: str, found: str, found_pos: Pos):
            self.description = (
                f"{CM().YELLOW}UnexpectedCharacter{CM().RESET_ALL}: No terminal "
                f"matches {CM().BLUE}'{found}'{CM().RESET_ALL} in the current lexical context of "
                f"{CM().RED}{expected}{CM().RESET_ALL}"
            )
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class UnexpectedToken(Exception):
        def __init__(self, expected: str, found: Token, found_pos: Pos):
            self.description = (
                f"{CM().YELLOW}UnexpectedToken{CM().RESET_ALL}: Expected e.g. {expected}"
                f", found {CM().BLUE}'{found}'{CM().RESET_ALL}"
            )
            self.expected = expected
            self.found = found
            self.found_pos = found_pos

    class UnexpectedEOF(Exception):
        def __init__(self, expected: str, last_pos: Pos):
            self.description = (
                f"{CM().YELLOW}UnexpectedEOF{CM().RESET_ALL}: Unexpected "
                f"end-of-file, expected e.g. {expected}"
            )
            self.expected = expected
            self.last_pos = last_pos

    class UnknownIdentifier(Exception):
        """If Token shouldn't syntactically appear at this position"""

        def __init__(self, found: str, found_pos: Pos):
            self.description = (
                f"{CM().YELLOW}UnknownIdentifierError{CM().RESET_ALL}: Identifier "
                f"'{found}' wasn't declared yet"
            )
            self.found = found
            self.found_pos = found_pos

    class TooLargeLiteral(Exception):
        """If the literal assigned to a variable is too large for the datatype of
        the variable"""

        def __init__(self, found, found_pos, found_symbol_type, found_from, found_to):
            self.description = f"{CM().YELLOW}TooLargeLiteralError{CM().RESET_ALL}: Literal '{found}' is too large"
            self.found = found
            self.found_pos = found_pos
            self.found_symbol_type = found_symbol_type
            self.found_from = found_from
            self.found_to = found_to

    class Redeclaration(Exception):
        def __init__(self, found, found_pos, first, first_pos):
            self.description = f"{CM().YELLOW}RedefinitionError{CM().RESET_ALL}: Redefinition of '{found}'"
            self.found = found
            self.found_pos = found_pos
            self.first = first
            self.first_pos = first_pos

    class ConstReassignment(Exception):
        def __init__(self, found, found_pos, first_pos):
            self.description = (
                f"{CM().YELLOW}ConstReassignmentError{CM().RESET_ALL}: Can't reassign a new "
                f"value to named constant '{found}'"
            )
            self.found = found
            self.found_pos = found_pos
            self.first_pos = first_pos

    class NoMainFunction(Exception):
        """If there's no main function within the given file"""

        def __init__(self, fname):
            self.description = (
                f"{CM().YELLOW}NoMainFunctionError{CM().RESET_ALL}: There's no main function"
                f" in file '{fname}'"
            )

    class MoreThanOneMainFunction(Exception):
        def __init__(self, first_pos, second_pos):
            self.description = (
                f"{CM().YELLOW}MoreThanOneMainFunctionError{CM().RESET_ALL}: There're at "
                "least two main functions"
            )
            self.first_pos = first_pos
            self.second_pos = second_pos

    class BugInCompiler(Exception):
        def __init__(self, fun_name, args):
            self.description = (
                f"{CM().YELLOW}BugInCompiler{CM().RESET_ALL}: Error in function "
                f"{CM().BLUE}'{fun_name}'{CM().RESET_ALL} with {args}. This error should "
                "not be possible, but it occured. Please report this issue under "
                f"{CM().RED}https://github.com/matthejue/PicoC-Compiler/issues/new/choose{CM().RESET_ALL}"
            )
