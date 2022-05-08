from sys import exit
from errors import Errors
import global_vars
from colormanager import ColorManager as CM
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedEOF,
    UnexpectedInput,
)


class ErrorHandler:
    """Output a detailed error message"""

    def __init__(self, code):
        self.code = code
        #  self.splitted_code = list(
        #      filter(
        #          lambda line: line,
        #          map(lambda line: line.strip(), code_with_file.split("\n")),
        #      )
        #  )

    def handle(self, function, *args):
        try:
            rtrn_val = function(*args)
        except UnexpectedToken as e:
            print(e)
            exit(0)
        except UnexpectedCharacters as e:
            print(e)
            print(e.allowed)
            exit(0)
        except UnexpectedEOF as e:
            print(e)
            exit(0)
        except Errors.InvalidCharacterError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.UnclosedCharacterError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.NoApplicableRuleError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.point_at(e.found_pos, e.expected)
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.MismatchedTokenError as e:
            error_header = self._error_header(e.found_pos, e.description)
            expected_pos = self._find_space_after_previous_token(e.found_pos)
            error_screen = AnnotationScreen(self.code, expected_pos[0], e.found_pos[0])
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
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            print("\n" + error_header + str(error_screen))
            exit(0)
        except Errors.TooLargeLiteralError as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
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
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            note_header = self._error_header(
                e.first_pos, f"{CM().MAGENTA}Note{CM().RESET}: Already defined here:"
            )
            error_screen_2 = AnnotationScreen(self.code, e.first_pos[0], e.first_pos[0])
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
            error_screen = AnnotationScreen(self.code, e.found_pos[0], e.found_pos[0])
            error_screen.mark(e.found_pos, len(e.found))
            note_header = self._error_header(
                e.first_pos,
                f"{CM().MAGENTA}Note{CM().RESET}: Constant identifier was initialised here:",
            )
            error_screen_2 = AnnotationScreen(self.code, e.first_pos[0], e.first_pos[0])
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
            error_screen = AnnotationScreen(self.code, e.first_pos[0], e.first_pos[0])
            error_screen.mark(e.first_pos, 4)
            note_header = self._error_header(
                e.second_pos,
                f"{CM().MAGENTA}Note{CM().RESET}: Second main function defined here:",
            )
            error_screen_2 = AnnotationScreen(
                self.code, e.second_pos[0], e.second_pos[0]
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

    def _error_header(self, pos, descirption):
        if not pos:
            return CM().BRIGHT + descirption + CM().RESET_ALL + "\n"
        return (
            CM().BRIGHT
            + global_vars.args.infile
            + ":"
            + str(pos[0])
            + ":"
            + str(pos[1])
            + ": "
            + descirption
            + CM().RESET_ALL
            + "\n"
        )

    def __repr__(self):
        return str(self.code)


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

        self.context_below = code[row_to + 1 : row_to + 1 + global_vars.args.sight]

        self.marked_lines = []
        self.row_from = row_from
        self.row_to = row_to

    def point_at(self, pos, word):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "^", pos[1], CM().RED
        )
        self.screen[3 * rel_row + 2] = overwrite(
            self.screen[3 * rel_row + 2], word, pos[1], CM().RED
        )
        self.marked_lines += [3 * rel_row + 1, 3 * rel_row + 2]

    def mark(self, pos, length):
        rel_row = pos[0] - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "~" * length, pos[1], CM().BLUE
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
