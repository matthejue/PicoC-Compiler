from sys import exit
from errors import Errors
import global_vars


class ErrorHandler:
    """Output a detailed error message"""

    SOF_CHAR = 'SOF'

    def __init__(self, fname, finput):
        self.fname = fname
        self.finput = finput

    def __repr__(self, ):
        return str(self.finput)

    def handle(self, function, *args):
        try:
            function(*args)
        except Errors.InvalidCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.UnclosedCharacterError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.NoApplicableRuleError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.MismatchedTokenError as e:
            error_header = self._error_header(e) + '\n'
            expected_pos = self._find_space_after_previous_token(e.found_pos)
            error_screen = ErrorScreen(self.finput, expected_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.point_at(expected_pos, e.expected)
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.TastingError as e:
            error_header = self._error_header(e) + '\n'
            print('\n' + error_header)
            exit(0)
        except Errors.UnknownIdentifierError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.TooLargeLiteralError as e:
            error_header = self._error_header(e) + '\n'
            error_screen = ErrorScreen(self.finput, e.found_pos[0],
                                       e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print('\n' + error_header + str(error_screen))
            exit(0)
        except Errors.NoMainFunctionError as e:
            error_header = e.description + '\n'
            print('\n' + error_header)
            exit(0)
        except Errors.NotImplementedYetError as e:
            error_header = e.description + '\n'
            print('\n' + error_header)
            exit(0)

    def _error_header(self, error):
        return self.fname + ':' + str(error.found_pos[0]) + ':' + str(
            error.found_pos[1]) + ': ' + error.description

    def _find_space_after_previous_token(self, pos):
        row, col = pos[0], pos[1]
        while True:
            old_row = row
            row, col = self._previous_char(row, col)

            # comments should be overwritten with space
            if old_row != row:
                self.finput[row] = self._remove_comments(self.finput[row])

            if self.finput[row][col] not in " \t":
                break
        return (row, col + 1)

    def _remove_comments(self, line):
        """checks whether there comes a comment while going back and if yes
        return the position where the comment starts
        """
        col = len(line) - 1
        while col > 0:
            if line[col - 1] == '/' and line[col] == '/':
                col -= 1
                line = overwrite(line, ' ' * (len(line) - col), col)
            elif line[col - 1] == '*' and line[col] == '/':
                col_to = col
                col -= 2
                while col > 0:
                    if line[col - 1] == '/' and line[col] == '*':
                        col -= 1
                        line = overwrite(line, ' ' * (col_to - col + 1), col)
                        break
                    col -= 1
                else:
                    line = overwrite(line, ' ' * (col_to + 1), 0)
            elif line[col - 1] == '/' and line[col] == '*':
                col_from = col - 1
                line = overwrite(line, ' ' * (len(line) - col_from), col_from)
            col -= 1
        return line

    def _previous_char(self, row, col):
        # in contrast to the lexer the row and col vars are always kept as
        # local variables they're only releavnt for the function
        # _find_space_after_previous_token

        # next column or next row
        # the first row is for the filename
        if col > 0:
            col -= 1
        elif col == 0 and row > 1:
            row -= 1
            col = len(self.finput[row]) - 1
        elif col == 0 and row == 1:
            col -= 1

        #  if (col == -1 and row == 1):
        #  lc = self.SOF_CHAR
        #  else:
        #  lc = self.finput[row][col]
        return row, col


class ErrorScreen:
    def __init__(self, finput, row_from, row_to):
        # because the filename gets pasted in the first line of file content
        context_from = row_from - global_vars.args.sight if row_from -\
            global_vars.args.sight > 0 else 1
        self.context_above = finput[context_from:row_from]

        self.screen = []
        for line in finput[row_from:row_to + 1]:
            # len(line)+1 to be able to show expected semicolons
            self.screen += [line, ' ' * (len(line) + 1), ' ' * (len(line) + 1)]

        self.context_below = finput[row_to + 1:row_to + 1 +
                                    global_vars.args.sight]

        self.marked_lines = []
        self.row_from = row_from
        self.row_to = row_to

    def point_at(self, pos, word):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(self.screen[3 * rel_row + 1],
                                                 '^', pos[1])
        self.screen[3 * rel_row + 2] = overwrite(self.screen[3 * rel_row + 2],
                                                 word, pos[1])
        self.marked_lines += [3 * rel_row + 1, 3 * rel_row + 2]

    def mark(self, pos, length):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(self.screen[3 * rel_row + 1],
                                                 '~' * length, pos[1])
        # mark line to
        self.marked_lines += [3 * rel_row + 1]

    def filter(self, ):
        # -2 da man idx's bei 0 anfängen und man zwischen 0 und 2 usw. sein will
        for i in set(range(0, len(self.screen))) - set(
                range(0, len(self.screen), 3)) - set(self.marked_lines):
            del self.screen[i]

    def undo(self, ):
        ...

    def __repr__(self, ):
        acc = ""

        for line in self.context_above + self.screen + self.context_below:
            acc += line + '\n'

        return acc


def overwrite(old, replace_with, idx):
    return old[:idx] + replace_with + old[idx + len(replace_with):]
