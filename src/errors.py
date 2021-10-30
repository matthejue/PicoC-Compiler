from sys import exit
# because of circular import
import lexer
from enum import Enum


class InvalidCharacterError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""

    def __init__(self, value, position):
        self.description = f"InvalidCharacterError: "\
            f"'{value}' is not a permitted character"
        super().__init__(self.description)
        self.expected = None
        self.found = lexer.Token(
            lexer.TT.IDENTIFIER, value=value, position=position)


class NoApplicableRuleError(Exception):

    """If no rule is applicable in a situation where several undistinguishable
    alternatives are possible"""

    def __init__(self, expected, found):
        self.description = f"NoApplicableRuleError: Expected '{expected}'"\
            f", found '{found.value}'"
        super().__init__(self.description)
        self.expected = None
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


class States(Enum):

    """Special States for the ErrorHandler"""

    ONLY_FOUND = -1


class ErrorHandler:

    """Output a detailed error message"""

    def __init__(self, grammar):
        self.grammar = grammar

    def handle(self, function):
        error_message = ""
        try:
            function()
        except InvalidCharacterError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_found(
                States.ONLY_FOUND.value, e) + '\n'
            print(error_message)
            exit(0)
        except NoApplicableRuleError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_found(
                States.ONLY_FOUND.value, e) + '\n'
            print(error_message)
            exit(0)
        except MismatchedTokenError as e:
            error_message += self._error_message_header(e) + '\n'

            (row, column) = self._find_white_space_before_last_token(e)
            if row < e.found.position[0]:
                error_message += self._point_at_expected(
                    (row, column), e) + '\n'

                error_message += self._point_at_found(States.ONLY_FOUND.value,
                                                      e) + '\n'
            else:
                error_message += self._point_at_found(column,  e) + '\n'
            print(error_message)
            exit(0)
        except UnknownIdentifierError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_found(States.ONLY_FOUND.value, e)\
                + '\n'
            print(error_message)
            exit(0)

    def _error_message_header(self, error):
        return self.grammar.lexer.fname + ':' +\
            str(error.found.position[0]) + ':' + str(error.found.position[1]) \
            + ': ' + error.description

    def _point_at_expected(self, expected, error):
        # line with exptected symbol
        line = self.grammar.lexer.input[expected[0]] + '\n'
        # positionize expected symbol at the right position beneath with a
        # arrow pointing on it
        line += ' ' * expected[1] + '^' + '\n'
        line += ' ' * expected[1] + error.expected + '\n'
        for i in range(expected[0]+1, error.found.position[0]):
            line += self.grammar.lexer.input[i]
        return line

    def _point_at_found(self, expected_column, error):
        # TODO: Was ist wenn sich ein Token über mehrere Zeilen erstreck mit ^~
        line = self.grammar.lexer.input[error.found.position[0]] + '\n'
        if expected_column == error.found.position[1]:
            line += ' ' * expected_column + '^' + '\n'
            return line + ' ' * expected_column +\
                error.expected + '\n'
        elif expected_column >= 0:
            line += ' ' * (expected_column) + '^' + \
                ' ' * (error.found.position[1]-expected_column-1) +\
                '~' * len(error.found.value) + '\n'
            return line + ' ' * expected_column + error.expected + '\n'
        elif expected_column == States.ONLY_FOUND.value:
            return line + ' ' * error.found.position[1] +\
                '~' * len(error.found.value) + '\n'

    def _find_white_space_before_last_token(self, e):
        # TODO: Don't forget to remove this improvised conditional breakpoint
        import globals
        if globals.test_name == "single line comment":
            if globals.test_name == "single line comment":
                pass
        (row, column) = (e.found.position[0], e.found.position[1])
        while True:
            # comments should be overjumped
            res = self._check_for_comment(row, column)
            if res:
                (row, column) = res
            # TODO: make it more efficient by not chekcing a line several 'times'

            (row, column) = self._calculate_previous_row_column(row, column)
            if self.grammar.lexer.input[row][column] not in " \t":
                break
        return (row, column+1)

    def _check_for_comment(self, row, column):
        """checks whether there comes a comment while going back and if yes
        return the position where the comment starts
        """
        while True:
            (row, column) = self._calculate_previous_row_column(row, column)
            if self._check_words(["//", "/*"], row, column):
                break
        (row, column) = self._calculate_previous_row_column(row, column)
        return (row, column)

    def _check_words(self, patterns, row, column):
        match_pattern_results = []
        for pattern in patterns:
            single_match_results = []
            for char in reversed(pattern):
                single_match_results += [self.grammar.lexer.input[row]
                                         [column] == char]
                column -= column
            match_pattern_results += [all(single_match_results)]
        return any(match_pattern_results)

    def _calculate_previous_row_column(self, row, column):
        if column - 1 >= 0:
            column -= 1
        else:
            row -= 1
            column = len(self.grammar.lexer.input[row]) - 1
        return (row, column)
