from sys import exit
from errors import Errors, Range, Pos
import global_vars
from colormanager import ColorManager as CM
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedEOF,
)
from lark import Lark, Token
import compiler
import os
import itertools

MAP_TO_TERMINAL = {
    "NUM": "number",
    "CHAR": "character",
    "NAME": "identifier",
    "NEG": "'~'",
    "NOT": "'!'",
    "SUB_MINUS": "'-'",
    "ADD": "'+'",
    "MUL": "'*'",
    "DIV": "'/'",
    "MOD": "'%'",
    "OPLUS": "'^'",
    "AND": "'&'",
    "OR": "'|'",
    "EQ": "'=='",
    "NEQ": "'!='",
    "LT": "'<'",
    "LTE": "'<='",
    "GT": "'>'",
    "GTE": "'>='",
    "INT_DT": "'int'",
    "CHAR_DT": "'char'",
    "VOID_DT": "'void'",
    "STRUCT": "'struct'",
    "IF": "'if'",
    "ELSE": "'else'",
    "WHILE": "'while'",
    "DO": "'do'",
    # tokennames from https://github.com/lark-parser/lark/blob/86c8ad41c9e5380e30f3b63b894ec0b3cb21a20a/lark/load_grammar.py#L34
    "DOT": "'.'",
    "COMMA": "','",
    "SEMICOLON": "';'",
    "STAR": "'*'",
    "LPAR": "'('",
    "RPAR": "')'",
    "LBRACE": "'{'",
    "RBRACE": "'}'",
    "LSQB": "'['",
    "RSQB": "']'",
}

MAX_EXPECTED_TOKENS = 5


class ErrorHandler:
    """Output a detailed error message"""

    def __init__(self, code_with_file):
        self.code_with_file = code_with_file
        self.split_code = code_with_file.split("\n")

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
            self._error_heading()
            expected_str = set_to_str(e.expected)
            # -1 because lark starts counting from 1
            e = Errors.UnexpectedTokenError(
                expected_str,
                e.token.value,
                Range(
                    Pos(e.token.line - 1, e.token.column - 1),
                    Pos(e.token.end_line - 1, e.token.end_column - 1),
                ),
            )
            error_header = self._error_header(e.found_range.start_pos, e.description)
            prev_token = self._find_prev_token(e.found_range.start_pos)
            # -2 because ranges always end with + 1 of the actual position and
            # because Lark starts counting with 1
            expected_pos = Pos(prev_token.end_line - 1, prev_token.end_column - 2 + 1)
            error_screen = AnnotationScreen(
                self.split_code,
                expected_pos.line,
                e.found_range.end_pos.line,
            )
            error_screen.mark(e.found_range.start_pos, len(e.found))
            if e.found_range.start_pos == expected_pos:
                error_screen.clear(1)
            error_screen.point_at(expected_pos, expected_str)
            error_screen.filter()
            self._write_error_to_file(
                error_header + str(error_screen) + "\n\n", e.__class__.__name__
            )
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

    def _error_heading(self):
        terminal_width = os.get_terminal_size().columns
        print(compiler.subheading("Error", terminal_width, "-"))

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
        )

    def _find_prev_token(self, pos: Pos) -> Token:
        parser = Lark.open(
            "./src/concrete_syntax.lark",
            lexer="basic",
            priority="invert",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )
        tokens = list(parser.lex(self.code_with_file))

        # find token with same position
        for (i, token) in enumerate(tokens):
            # -1 because Lark starts counting from 1
            if token.line - 1 == pos.line and token.column - 1 == pos.column:
                break
        return tokens[i - 1]

    def _write_error_to_file(self, error_str, error_name):
        print(error_str)
        if global_vars.outbase:
            with open(global_vars.outbase + ".out", "w", encoding="utf-8") as fout:
                fout.write(error_name + "\n")
            with open(global_vars.outbase + ".error", "w", encoding="utf-8") as fout:
                fout.write(error_str)

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

    def clear(self, row):
        self.screen[row] = " " * (len(self.screen[row]) + 1)

    def __repr__(self):
        acc = "\n"

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


def set_to_str(tokenset):
    return " or ".join(
        MAP_TO_TERMINAL.get(elem, elem)
        for elem in itertools.islice(tokenset, MAX_EXPECTED_TOKENS + 1)
        if "ANON" not in elem
    )
