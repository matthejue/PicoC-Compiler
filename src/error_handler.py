from sys import exit
from enum import Enum
from errors import Errors
from lexer import Lexer


class States(Enum):
    """Special States for the ErrorHandler"""

    ONLY_FOUND = -1


class ErrorHandler:
    """Output a detailed error message"""

    LENGTH_COMMENT_TOKEN = 2

    def __init__(self, fname, finput):
        self.fname = fname
        self.finput = finput

    def handle(self, function):
        try:
            function()
        except Errors.InvalidCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            print(error_header + error_screen)
            exit(0)
        except Errors.UnclosedCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            print(error_header + error_screen)
            exit(0)
        except Errors.NoApplicableRuleError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            print(error_header + error_screen)
            exit(0)
        except Errors.MismatchedTokenError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            print(error_header + error_screen)
            exit(0)
        except Errors.TastingError as e:
            error_header = self._error_header(e) + '\n'
            print(error_header)
            exit(0)
        except Errors.UnknownIdentifierError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            print(error_header + error_screen)
            exit(0)
        except Errors.TooLargeLiteralError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            print(error_header + error_screen)
            exit(0)
        except Errors.NoMainFunctionError as e:
            error_header = self._error_header(e) + '\n'
            print(error_header)
            exit(0)

    def _error_header(self, error):
        return self.fname + ':' + str(error.found_pos[0]) + ':' + str(
            error.found_pos[1]) + ': ' + error.description

    def _find_white_space_before_last_token(self, e):
        row, column = e.found.position[0], e.found.position[1]
        while True:
            (row, column) = self._calculate_previous_row_column(row, column)

            # comments should be overjumped
            res = self._check_for_comment(row, column)
            if res:
                (row, column) = res

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
        return self._calculate_previous_row_column(
            row, column - self.LENGTH_COMMENT_TOKEN + 1)

    def _check_words(self, patterns, row, column):
        # check all patterns
        for pattern in patterns:
            single_match_results = []
            column_copy = column
            # check every letter of single pattern
            for char in reversed(pattern):
                single_match_results += [
                    self.grammar.lexer.input[row][column_copy] == char
                ]
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


class ErrorScreen:
    def __init__(self, finput, row_from, row_to):
        self.screen = []
        for line in finput[row_from:row_to + 1]:
            self.screen += [line, ' ' * len(line), ' ' * len(line)]

    def point_at(self, pos, word):
        self.screen[3 * pos[0] + 1] = replace(self.screen[3 * pos[0] + 1], '^',
                                              pos[1])
        self.screen[3 * pos[0] + 2] = replace(self.screen[3 * pos[0] + 2],
                                              word, pos[1])
        self.screen[3 * pos[0] + 1] += "m"

    def mark(self, pos, length):
        self.screen[3 * pos[0] + 1] = replace(self.screen[3 * pos[0] + 1],
                                              '~' * length, pos[1])
        # mark line to
        self.screen[3 * pos[0] + 1] += "m"

    def __repr__(self, ):
        for i in range(1, len(self.screen) - 1, -3):
            if self.screen[i] != 'm':
                del self.screen[i]
                del self.screen[i + 1]
        return self.screen


def replace(old, replace_with, idx):
    return old[:idx] + replace_with + old[idx + len(replace_with):]
