from sys import exit
from enum import Enum
from errors import InvalidCharacterError, UnclosedCharacterError,\
    MismatchedTokenError, NoApplicableRuleError, UnknownIdentifierError


class States(Enum):

    """Special States for the ErrorHandler"""

    ONLY_FOUND = -1


class ErrorHandler:

    """Output a detailed error message"""

    LENGTH_COMMENT_TOKEN = 2

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
        except UnclosedCharacterError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_found(
                e.found.position[1], e) + '\n'
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
                error_message += self._point_at_exptected(
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

    def _point_at_exptected(self, exptected_pos, error):
        # line with exptected symbol
        line = self.grammar.lexer.input[exptected_pos[0]] + '\n'
        # positionize exptected_pos symbol at the right position beneath with a
        # arrow pointing on it
        line += ' ' * exptected_pos[1] + '^' + '\n'
        line += ' ' * exptected_pos[1] + error.exptected + '\n'
        for i in range(exptected_pos[0]+1, error.found.position[0]):
            line += self.grammar.lexer.input[i]
        return line

    def _point_at_found(self, expected_column, error):
        # TODO: Was ist wenn sich ein Token über mehrere Zeilen erstreck mit ^~
        line = self.grammar.lexer.input[error.found.position[0]] + '\n'
        if expected_column == error.found.position[1]:
            line += ' ' * expected_column + '^' + '\n'
            return line + ' ' * expected_column +\
                error.expected + '\n'
        if expected_column >= 0:
            line += ' ' * (expected_column) + '^' + \
                ' ' * (error.found.position[1]-expected_column-1) +\
                '~' * len(error.found.value) + '\n'
            return line + ' ' * expected_column + error.expected + '\n'
        return line + ' ' * error.found.position[1] +\
            '~' * len(error.found.value) + '\n'

    def _find_white_space_before_last_token(self, e):
        (row, column) = self._calculate_previous_row_column(
            e.found.position[0], e.found.position[1])
        while True:
            # comments should be overjumped
            res = self._check_for_comment(row, column)
            if res:
                (row, column) = res

            (row, column) = self._calculate_previous_row_column(row, column)
            if self.grammar.lexer.input[row][column] not in " \t":
                break
        return (row, column + 1)

    def _check_for_comment(self, row, column):
        """checks whether there comes a comment while going back and if yes
        return the position where the comment starts
        """
        while column >= self.LENGTH_COMMENT_TOKEN - 1:
            if self._check_words(["//", "/*"], row, column):
                break
            column -= 1
        else:
            return None
        return (row, column - self.LENGTH_COMMENT_TOKEN + 1)

    def _check_words(self, patterns, row, column):
        # check all patterns
        for pattern in patterns:
            single_match_results = []
            column_copy = column
            # check every letter of single pattern
            for char in reversed(pattern):
                single_match_results += [self.grammar.lexer.input[row]
                                         [column_copy] == char]
                column_copy -= 1
            if all(single_match_results):
                return True
        return False

    def _calculate_previous_row_column(self, row, column):
        if column - 1 >= 0:
            column -= 1
        else:
            row -= 1
            column = len(self.grammar.lexer.input[row]) - 1
        return (row, column)
