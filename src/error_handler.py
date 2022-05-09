from sys import exit
from errors import Errors, Range, Pos
import global_vars
from colormanager import ColorManager as CM
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedEOF,
)


class ErrorHandler:
    """Output a detailed error message"""

    def __init__(self, code_with_file):
        self.split_code = code_with_file.split("\n")
        # in case there's a multiline inline comment that spreads over more then 2 lines
        self.multiline_comment_started = False
        # list of removed comments to undo the removing later
        self.removed_comments = [(0, 0, "")]

    def handle(self, function, *args):
        try:
            rtrn_val = function(*args)
        except UnexpectedCharacters as e:
            #  e = Errors.UnexpectedCharacterError(e.allowed, e.char, (e.line, e.column))
            #  error_header = self._error_header(e.found_pos, e.description)
            #  error_screen = AnnotationScreen(self.split_code, e.found_pos[0], e.found_pos[0])
            #  error_screen.mark(e.found_pos, len(e.found))
            #  error_screen.filter()
            #  print("\n" + error_header + str(error_screen))
            #  print("\n" + error_header)
            exit(0)
        except UnexpectedToken as e:
            e = Errors.UnexpectedTokenError(
                e.expected,
                e.token.value,
                Range(
                    Pos(e.token.line - 1, e.token.column - 1),
                    Pos(e.token.end_line - 1, e.token.end_column - 1),
                ),
            )
            error_header = self._error_header(e.found_range.start_pos, e.description)
            expected_pos = self._find_space_after_previous_token(
                (e.found_range.start_pos.line, e.found_range.start_pos.column)
            )
            error_screen = AnnotationScreen(
                self.split_code,
                e.found_range.start_pos.line,
                e.found_range.end_pos.line,
            )
            error_screen.mark(e.found_range.start_pos, len(e.found))
            if e.found_range.start_pos == expected_pos:
                pos = expected_pos
                row_from = expected_pos[0]
                rel_row = pos[0] - row_from
                error_screen.clear(rel_row + 1, pos[1])
            error_screen.point_at(Pos(expected_pos[0], expected_pos[1]), "expected")
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except UnexpectedEOF as e:
            exit(0)
        except Errors.InvalidCharacterError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.UnclosedCharacterError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.NoApplicableRuleError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.MismatchedTokenError as e:
            error_header = self._error_header(e.found_pos, e.description)
            expected_pos = self._find_space_after_previous_token(e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code, expected_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            if e.found_pos == expected_pos:
                pos = expected_pos
                row_from = expected_pos[0]
                rel_row = pos[0] - row_from
                error_screen.clear(rel_row + 1, pos[1])
            error_screen.point_at(expected_pos, e.expected)
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.TastingError as e:
            error_header = self._error_header(None, e.description)
            print("\n" + error_header)
            exit(0)
        except Errors.UnknownIdentifierError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.TooLargeLiteralError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            node_header = self._error_header(
                None,
                f"{CM().MAGENTA}Note{CM().RESET}: The max size of a literal for a {e.found_symbol_type} is "
                f"in range '{e.found_from}' to '{e.found_to}'",
            )
            error_screen.filter()
            print("\n" + error_header + str(error_screen) + node_header)
            exit(0)
        except Errors.RedefinitionError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            note_header = self._error_header(
                e.first_pos, f"{CM().MAGENTA}Note{CM().RESET}: Already defined here:"
            )
            error_screen_2 = AnnotationScreen(
                self.split_code, e.first_pos[0], e.first_pos[0]
            )
            error_screen_2.mark(e.first_pos, len(e.first))
            error_screen.filter()
            error_screen_2.filter()
            print(
                "\n"
                + error_header
                + str(error_screen)
                + note_header
                + str(error_screen_2)
            )
            exit(0)
        except Errors.ConstReassignmentError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            note_header = self._error_header(
                e.first_pos,
                f"{CM().MAGENTA}Note{CM().RESET}: Constant identifier was initialised here:",
            )
            error_screen_2 = AnnotationScreen(
                self.split_code, e.first_pos[0], e.first_pos[0]
            )
            error_screen_2.mark(e.first_pos, len(e.first))
            error_screen.filter()
            error_screen_2.filter()
            print(
                "\n"
                + error_header
                + str(error_screen)
                + note_header
                + str(error_screen_2)
            )
            exit(0)
        except Errors.NoMainFunctionError as e:
            error_header = e.description + "\n"
            print("\n" + error_header)
            exit(0)
        except Errors.MoreThanOneMainFunctionError as e:
            error_header = self._error_header(e.first_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.first_pos[0], e.first_pos[0]
            )
            error_screen.mark(e.first_pos, 4)
            note_header = self._error_header(
                e.second_pos,
                f"{CM().MAGENTA}Note{CM().RESET}: Second main function defined here:",
            )
            error_screen_2 = AnnotationScreen(
                self.split_code, e.second_pos[0], e.second_pos[0]
            )
            error_screen_2.mark(e.second_pos, 4)
            error_screen.filter()
            error_screen_2.filter()
            print(
                "\n"
                + error_header
                + str(error_screen)
                + note_header
                + str(error_screen_2)
            )
            exit(0)
        except Errors.NotImplementedYetError as e:
            error_header = e.description + "\n"
            print("\n" + error_header)
            exit(0)
        return rtrn_val

    def _error_header(self, pos: Pos, descirption):
        if not pos:
            return CM().BRIGHT + descirption + CM().RESET_ALL + "\n"
        return (
            CM().BRIGHT
            + global_vars.args.infile
            + ":"
            + str(pos.line)
            + ":"
            + str(pos.column)
            + ": "
            + descirption
            + CM().RESET_ALL
            + "\n"
        )

    def _find_space_after_previous_token(self, pos):
        row, col = pos[0], pos[1]
        self.split_code[row] = self._remove_comments(row)
        while row > 0:
            old_row = row
            row, col = self._previous_position(row, col)

            # comments should be overwritten with space
            if old_row != row:
                self.split_code[row] = self._remove_comments(row)
                if self.multiline_comment_started == True:
                    self._store_comment(row, 0, self.split_code[row])
                    self.split_code[row] = overwrite(
                        self.split_code[row], " " * len(self.split_code[row]), 0
                    )
            if self.split_code[row][col] not in " \t":
                break
        self._undo_removing_commments()
        return (row, col + 1)

    def _remove_comments(self, row):
        """checks whether there comes a comment while going back and if yes
        return the position where the comment starts
        """
        line = self.split_code[row]
        col = len(line) - 1
        while col > 0:
            if line[col - 1] == "/" and line[col] == "/":
                col -= 1
                self._store_comment(row, col, line[col : len(line)])
                line = overwrite(line, " " * (len(line) - col), col)
            elif line[col - 1] == "*" and line[col] == "/":
                col_to = col
                col -= 2
                while col > 0:
                    if line[col - 1] == "/" and line[col] == "*":
                        col -= 1
                        self._store_comment(row, col, line[col : col_to + 1])
                        line = overwrite(line, " " * (col_to - col + 1), col)
                        break
                    col -= 1
                else:
                    self._store_comment(row, 0, line[0 : col_to + 1])
                    line = overwrite(line, " " * (col_to + 1), 0)
                    self.multiline_comment_started = True
            elif line[col - 1] == "/" and line[col] == "*":
                col_from = col - 1
                self._store_comment(row, col_from, line[col_from : len(line)])
                line = overwrite(line, " " * (len(line) - col_from), col_from)
                self.multiline_comment_started = False
            col -= 1
        return line

    def _store_comment(self, row, col, comment):
        # The if is only necessary in case _remove_comments already emptied a
        # */ commment and in turn set multiline_comment_started to True. When
        # returning from this function The emptied comment would be copied again.
        if self.removed_comments[-1][0] != row:
            self.removed_comments += [(row, col, comment)]

    def _undo_removing_commments(self):
        for row, col, comment in self.removed_comments:
            self.split_code[row] = overwrite(self.split_code[row], comment, col)

    def _previous_position(self, row, col):
        # in contrast to the lexer the row and col vars are always kept as
        # local variables they're only releavnt for the function
        # _find_space_after_previous_token

        # next column or next row
        # the first row is for the filename
        if col > 0:
            col -= 1
        elif col == 0 and row > 1:
            row -= 1
            col = len(self.split_code[row]) - 1
        elif col == 0 and row == 1:
            row -= 1
        return row, col

    def __repr__(self):
        return self.split_code


class AnnotationScreen:
    def __init__(self, code, row_from, row_to):
        # because the filename gets pasted in the first line of file content
        context_from = (
            row_from - global_vars.args.sight
            if row_from - global_vars.args.sight > 0
            else 1
        )
        self.context_above = code[context_from:row_from]

        self.screen = []
        for line in code[row_from : row_to + 1]:
            # len(line)+1 to be able to show expected semicolons
            self.screen += [line, " " * (len(line) + 1), " " * (len(line) + 1)]

        self.context_below = code[
            row_to + 1 : row_to + 1 + (global_vars.args.sight + 1)
        ]

        self.marked_lines = []
        self.row_from = row_from
        self.row_to = row_to

    def point_at(self, pos: Pos, word):
        rel_row = pos.line - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "^", pos.column, CM().RED
        )
        self.screen[3 * rel_row + 2] = overwrite(
            self.screen[3 * rel_row + 2], word, pos.column, CM().RED
        )
        self.marked_lines += [3 * rel_row + 1, 3 * rel_row + 2]

    def mark(self, pos: Pos, length):
        rel_row = pos.line - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "~" * length, pos.column, CM().BLUE
        )
        self.marked_lines += [3 * rel_row + 1]

    def filter(self):
        # -2 da man idx's bei 0 anfängt und man zwischen 0 und 2 usw. sein will
        for i in sorted(
            set(range(0, len(self.screen)))
            - set(range(0, len(self.screen), 3))
            - set(self.marked_lines),
            reverse=True,
        ):
            del self.screen[i]

    def clear(self, row, col):
        self.screen[row] = overwrite(self.screen[row], " " * len(self.screen[row]), col)

    def __repr__(self):
        acc = ""

        for line in self.context_above + self.screen + self.context_below:
            acc += line + "\n"

        return acc


def overwrite(old, replace_with, idx, color=""):
    return (
        old[:idx]
        + color
        + replace_with
        + (CM().RESET if color else "")
        + old[idx + len(replace_with) :]
    )
