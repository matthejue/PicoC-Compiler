from sys import exit
import errors
from global_classes import Pos
import global_vars
from colormanager import ColorManager as CM
from global_funs import overwrite, tokennames_to_str
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedEOF,
)
from lark.lexer import Token
from lark.lark import Lark
from global_funs import subheading
import os
import sys
import traceback


class ErrorHandler:
    def __init__(self, code_with_file):
        self.code_with_file = code_with_file
        self.split_code = code_with_file.split("\n")

    def handle(self, function, *args):
        try:
            rtrn_val = function(*args)
        except UnexpectedCharacters as e:
            self._error_heading()
            prev_token = e.token_history[-1]
            expected_pos = Pos(prev_token.end_line - 1, prev_token.end_column - 2)
            expected_str = global_vars.TOKENNAME_TO_SYMBOL.get(
                prev_token.type, prev_token.type
            )
            e = errors.UnexpectedCharacter(
                expected_str,
                e.char,
                Pos(e.line - 1, e.column - 1),
            )
            error_header = self._error_header(e.description, e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code,
                expected_pos.line,
                e.found_pos.line,
            )
            error_screen.mark(e.found_pos, width=1)
            error_screen.point_at(expected_pos, "context of " + expected_str)
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except UnexpectedToken as e:
            self._error_heading()
            expected_str = tokennames_to_str(e.expected)
            # -1 because lark starts counting from 1
            e = errors.UnexpectedToken(
                expected_str,
                e.token.value,
                Pos(e.token.line - 1, e.token.column - 1),
            )
            error_header = self._error_header(e.description, e.found_pos)
            prev_token = self._find_prev_token(e.found_pos)
            # -2 because ranges always end with + 1 of the actual position and
            # because Lark starts counting with 1
            prev_pos = Pos(prev_token.end_line - 1, prev_token.end_column - 2 + 1)
            error_screen = AnnotationScreen(
                self.split_code,
                prev_pos.line,
                e.found_pos.line,
            )
            error_screen.mark(e.found_pos, len(e.found))
            if e.found_pos == prev_pos:
                error_screen.clear(1)
            error_screen.point_at(prev_pos, expected_str)
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except UnexpectedEOF as e:
            self._error_heading()
            expected_str = tokennames_to_str(e.expected)
            last_token = self._find_last_token()
            last_pos = Pos(last_token.end_line - 1, last_token.end_column - 2 + 1)
            e = errors.UnexpectedEOF(expected_str, last_pos)
            error_header = self._error_header(e.description, e.last_pos)
            error_screen = AnnotationScreen(
                self.split_code, last_pos.line, last_pos.line
            )
            error_screen.point_at(e.last_pos, expected_str)
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except (errors.UnknownIdentifier, errors.ConstAssign, errors.ConstRef) as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos.line, e.found_pos.line
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except errors.NotExactlyOneMainFunction as e:
            self._error_heading()
            error_header = self._error_header(e.description)
            self._output_error(error_header, e.__class__.__name__)
            exit(0)
        except errors.TooLargeLiteral as e:
            self._error_heading()
            error_header = self._error_header(e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos.line, e.found_pos.line
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except (errors.Redefinition, errors.Redeclaration) as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos.line, e.found_pos.line
            )
            error_screen.mark(e.found_pos, len(e.found))
            note_header = self._error_header(
                e.description2,
                e.first_pos,
            )
            error_screen_2 = AnnotationScreen(
                self.split_code, e.first_pos.line, e.first_pos.line
            )
            error_screen_2.mark(e.first_pos, len(e.found))
            error_screen.filter()
            error_screen_2.filter()
            self._output_error(
                error_header + str(error_screen) + note_header + str(error_screen_2),
                e.__class__.__name__,
            )
            exit(0)
        except errors.DatatypeMismatch as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.var_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.var_pos.line, e.var_pos.line
            )
            error_screen.mark_consider_colors(e.var_pos, len(e.var_name))
            if e.var_pos == e.expected_pos:
                error_screen.clear(1)
                error_screen.color_offset = 0
            error_screen.point_at(
                e.expected_pos,
                f"expected '{e.expected_datatype}', found '{e.var_context_datatype}'",
            )
            self.color_offset = 0
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except errors.NodeError as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.node_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.node_pos.line, e.node_pos.line
            )
            error_screen.point_at(e.node_pos, "")
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        # ---------------------------------------------------------------------
        except errors.TooLargeLiteral as e:
            error_header = self._error_header(e.found_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos[0], e.found_pos[0]
            )
            error_screen.mark(e.found_pos, len(e.found))
            node_header = self._error_header(
                None,
                f"{CM().MAGENTA}Note{CM().RESET_ALL}: The max size of a literal for a {e.found_symbol_type} is "
                f"in range '{e.found_from}' to '{e.found_to}'",
            )
            error_screen.filter()
            print("\n" + error_header + str(error_screen) + node_header)
            exit(0)
        except errors.NoMainFunction as e:
            error_header = e.description + "\n"
            print("\n" + error_header)
            exit(0)
        except errors.MoreThanOneMainFunction as e:
            error_header = self._error_header(e.first_pos, e.description)
            error_screen = AnnotationScreen(
                self.split_code, e.first_pos[0], e.first_pos[0]
            )
            error_screen.mark(e.first_pos, 4)
            note_header = self._error_header(
                e.second_pos,
                f"{CM().MAGENTA}Note{CM().RESET_ALL}: Second main function defined here:",
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
        except errors.BugInCompiler as e:
            self._error_heading()
            error_header = self._error_header(e.description)
            note_header = self._error_header(
                e.description2,
            )
            self._output_error(error_header + "\n" + note_header, e.__class__.__name__)
            exit(1)
        except errors.BugInInterpreter as e:
            self._error_heading()
            error_header = self._error_header(e.description)
            note_header = self._error_header(
                e.description2,
            )
            self._output_error(error_header + "\n" + note_header, e.__class__.__name__)

            traceback.print_exc()
            exit(1)
        return rtrn_val

    def _error_heading(self):
        terminal_width = os.get_terminal_size().columns if sys.stdin.isatty() else 79
        print(subheading("Error", terminal_width, "-"))

    def _error_header(self, description: str, pos=None):
        # description has to contain a CM().RESET_ALL somewhere
        if not pos:
            return CM().BRIGHT + global_vars.args.infile + ": " + description
        return (
            CM().BRIGHT
            + CM().WHITE
            + global_vars.args.infile
            + ":"
            + CM().MAGENTA
            + str(pos.line)
            + ":"
            + str(pos.column)
            + ": "
            + description
        )

    def _find_prev_token(self, pos: Pos) -> Token:
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
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

    def _find_last_token(self) -> Token:
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="invert",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )
        tokens = list(parser.lex(self.code_with_file))
        return tokens[-1]

    def _output_error(self, error_str, error_name):
        print(error_str)
        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".out", "w", encoding="utf-8"
            ) as fout:
                fout.write(error_name + "\n")
            with open(
                global_vars.path + global_vars.basename + ".error",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(error_str)
        if global_vars.args.traceback:
            traceback.print_exc()

    def __repr__(self):
        return self.split_code


class AnnotationScreen:
    def __init__(self, code, row_from, row_to):
        # because the filename gets pasted in the first line of file content
        context_from = (
            row_from - global_vars.args.lines
            if row_from - global_vars.args.lines > 0
            else 1
        )
        self.context_above = code[context_from:row_from]

        self.screen = []
        for line in code[row_from : row_to + 1]:
            # len(line)+1 to be able to show expected semicolons
            self.screen += [line, " " * (len(line) + 1), " " * (len(line) + 1)]

        self.context_below = code[
            row_to + 1 : row_to + 1 + (global_vars.args.lines + 1)
        ]

        self.marked_lines = []
        self.row_from = row_from
        self.row_to = row_to

        # if a line was e.g. marked before with colors, the color ansi escape
        # sequences take up extra space that has to be consideres when drawing
        # afterwards
        self.color_offset = 0

    def point_at(self, pos: Pos, word):
        rel_row = pos.line - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "^", pos.column + self.color_offset, CM().RED
        )
        self.screen[3 * rel_row + 2] = overwrite(
            self.screen[3 * rel_row + 2], word, pos.column, CM().RED
        )
        self.marked_lines += [3 * rel_row + 1, 3 * rel_row + 2]

    def mark(self, pos: Pos, width: int):
        rel_row = pos.line - self.row_from
        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "~" * width, pos.column, CM().RED
        )
        self.marked_lines += [3 * rel_row + 1]

    def mark_consider_colors(self, pos: Pos, width: int):
        rel_row = pos.line - self.row_from

        len_line_before = len(self.screen[3 * rel_row + 1])

        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "~" * width, pos.column, CM().RED
        )
        self.marked_lines += [3 * rel_row + 1]

        self.color_offset = len(self.screen[3 * rel_row + 1]) - len_line_before

    def filter(self):
        # -2 da man idx's bei 0 anfängt und man zwischen 0 und 2 usw. sein will
        for i in sorted(
            set(range(0, len(self.screen)))
            - set(range(0, len(self.screen), 3))
            - set(self.marked_lines),
            reverse=True,
        ):
            del self.screen[i]

    def clear(self, rel_line):
        self.screen[rel_line] = " " * (len(self.screen[rel_line]) + 1)

    def __repr__(self):
        acc = "\n"

        for line in self.context_above + self.screen + self.context_below:
            acc += line + "\n"

        return acc[:-1]
