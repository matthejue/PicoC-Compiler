from sys import exit
from errors import Errors
import global_vars


class ErrorHandler:
    """Output a detailed error message"""

    LENGTH_COMMENT_TOKEN = 2

    def __init__(self, fname, finput):
        self.fname = fname
        self.finput = finput

    def handle(self, function, *args):
        try:
            function(*args)
        except Errors.InvalidCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print(error_header + str(error_screen))
            exit(0)
        except Errors.UnclosedCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print(error_header + str(error_screen))
            exit(0)
        except Errors.NoApplicableRuleError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print(error_header + str(error_screen))
            exit(0)
        except Errors.MismatchedTokenError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print(error_header + str(error_screen))
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
            error_screen.filter()
            print(error_header + str(error_screen))
            exit(0)
        except Errors.TooLargeLiteralError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print(error_header + str(error_screen))
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

        self.context_above = finput[row_from - global_vars.args.sight:row_from]

        self.screen = []
        for line in finput[row_from:row_to + 1]:
            self.screen += [line, ' ' * len(line), ' ' * len(line)]

        self.context_below = finput[row_to + 1:row_to + 1 +
                                    global_vars.args.sight]

        self.not_emtpy_marked = []
        self.row_from = row_from
        self.row_to = row_to

    def point_at(self, pos, word):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = replace(self.screen[3 * rel_row + 1],
                                               '^', pos[1])
        self.screen[3 * rel_row + 2] = replace(self.screen[3 * rel_row + 2],
                                               word, pos[1])
        self.not_emtpy_marked += [3 * rel_row + 1]

    def mark(self, pos, length):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = replace(self.screen[3 * rel_row + 1],
                                               '~' * length, pos[1])
        # mark line to
        self.not_emtpy_marked += [3 * rel_row + 1]

    def filter(self, ):
        # -2 da man idx's bei 0 anfängen und man zwischen 0 und 2 usw. sein will
        for i in range(len(self.screen) - 2, 0, -3):
            if i not in self.not_emtpy_marked:
                del self.screen[i + 1]
                del self.screen[i]

    def __repr__(self, ):
        acc = ""

        for line in self.context_above + self.screen + self.context_below:
            acc += line + '\n'

        return acc


def replace(old, replace_with, idx):
    return old[:idx] + replace_with + old[idx + len(replace_with):]
