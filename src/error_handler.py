from sys import exit
import errors
from util_classes import Pos
import global_vars
from colormanager import ColorManager as CM
from util_funs import overwrite, tokennames_to_str, subheading
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedToken,
    UnexpectedEOF,
)
from lark.lexer import Token
from lark.lark import Lark
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
                error_screen.clear(0)
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
        except (errors.UnknownIdentifier, errors.ConstAssign) as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos.line, e.found_pos.line
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except errors.UnknownAttribute as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.attr_pos)

            error_screen = AnnotationScreen(
                self.split_code,
                e.attr_pos.line,
                e.attr_pos.line,
            )
            error_screen.mark_consider_colors(e.var_pos, len(e.var_name))
            error_screen.point_at(
                e.attr_pos, f"is unknown in struct type '{e.struct_type_name}'"
            )
            note_header = self._error_header(
                e.description2,
                e.struct_type_pos,
            )

            error_screen2 = AnnotationScreen(
                self.split_code,
                e.struct_type_pos.line,
                e.struct_type_pos.line,
            )
            error_screen2.mark(e.struct_type_pos, len(e.struct_type_name))

            error_screen.filter()
            error_screen2.filter()
            self._output_error(
                error_header + str(error_screen) + note_header + str(error_screen2),
                e.__class__.__name__,
            )
            exit(0)
        except errors.NoMainFunction as e:
            self._error_heading()
            error_header = self._error_header(e.description)
            self._output_error(error_header, e.__class__.__name__)
            exit(0)
        except errors.TooLargeLiteral as e:
            self._error_heading()
            error_header = self._error_header(e.description, e.found_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.found_pos.line, e.found_pos.line
            )
            error_screen.mark(e.found_pos, len(e.found))
            error_screen.filter()
            self._output_error(error_header + str(error_screen), e.__class__.__name__)
            exit(0)
        except errors.PrototypeMismatch as e:
            self._error_heading()

            error_header = self._error_header(e.description, e.def_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.def_pos.line, e.def_param_pos.line
            )
            error_screen.mark_consider_colors(e.def_pos, len(e.def_name))
            if e.decl_param_pos == e.decl_pos:
                error_screen.clear(0)
                error_screen.color_offset = 0
            if e.decl_param_name == e.def_param_name:
                error_screen.point_at(e.def_param_pos, e.def_param_datatype)
            else:
                error_screen.point_at(
                    e.def_param_pos, f"not same identifier as '{e.decl_param_name}'"
                )

            error_header2 = self._error_header(e.description2, e.decl_pos)
            error_screen2 = AnnotationScreen(
                self.split_code, e.decl_pos.line, e.decl_param_pos.line
            )
            error_screen2.mark_consider_colors(e.decl_pos, len(e.def_name))
            if e.decl_param_pos == e.decl_pos:
                error_screen2.clear(0)
                error_screen2.color_offset = 0
            if e.decl_param_name == e.def_param_name:
                error_screen2.point_at(e.decl_param_pos, e.decl_param_datatype)
            else:
                error_screen2.point_at(
                    e.decl_param_pos, f"not same identifier as '{e.def_param_name}'"
                )

            error_screen.filter()
            error_screen2.filter()
            self._output_error(
                error_header + str(error_screen) + error_header2 + str(error_screen2),
                e.__class__.__name__,
            )
            exit(0)
        except errors.ArgumentMismatch as e:
            self._error_heading()

            error_header = self._error_header(e.description, e.fun_call_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.fun_call_pos.line, e.arg_pos.line
            )
            error_screen.mark_consider_colors(e.fun_call_pos, len(e.fun_name))
            error_screen.point_at(e.arg_pos, e.arg_datatype)

            error_header2 = self._error_header(e.description2, e.fun_pos)
            error_screen2 = AnnotationScreen(
                self.split_code, e.fun_pos.line, e.fun_param_pos.line
            )
            error_screen2.mark_consider_colors(e.fun_pos, len(e.fun_name))
            error_screen2.point_at(e.fun_param_pos, e.fun_param_datatype)

            error_screen.filter()
            error_screen2.filter()
            self._output_error(
                error_header + str(error_screen) + error_header2 + str(error_screen2),
                e.__class__.__name__,
            )
            exit(0)
        except errors.WrongNumberArguments as e:
            self._error_heading()

            error_header = self._error_header(e.description, e.fun_call_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.fun_call_pos.line, e.fun_call_pos.line
            )
            error_screen.mark_consider_colors(e.fun_call_pos, len(e.fun_name))

            error_header2 = self._error_header(e.description2, e.fun_pos)
            error_screen2 = AnnotationScreen(
                self.split_code, e.fun_pos.line, e.fun_pos.line
            )
            error_screen2.mark_consider_colors(e.fun_pos, len(e.fun_name))

            error_screen.filter()
            error_screen2.filter()
            self._output_error(
                error_header + str(error_screen) + error_header2 + str(error_screen2),
                e.__class__.__name__,
            )
            exit(0)
        except errors.WrongReturnType as e:
            self._error_heading()

            error_header = self._error_header(e.description, e.fun_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.fun_pos.line, e.last_stmt_pos.line
            )
            error_screen.mark(e.fun_pos, len(e.fun_name))
            if e.last_stmt_pos != e.fun_pos:
                error_screen.point_at(
                    e.last_stmt_pos,
                    e.found_return_type
                    if e.is_return
                    else "last statement is no return",
                )

            error_screen.filter()
            self._output_error(
                error_header + str(error_screen),
                e.__class__.__name__,
            )
            exit(0)
        except errors.ReDeclarationOrDefinition as e:
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
            error_header = self._error_header(e.description, e.identifier_pos)
            error_screen = AnnotationScreen(
                self.split_code, e.identifier_pos.line, e.identifier_pos.line
            )
            error_screen.mark_consider_colors(e.identifier_pos, len(e.identifier_name))
            if e.identifier_pos == e.expected_pos:
                error_screen.clear(0)
                error_screen.color_offset = 0
            error_screen.point_at(
                e.expected_pos,
                f"expected '{e.expected_datatype}', found '{e.identifier_context_datatype}'",
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
        match global_vars.args.extension:
            case "picoc":
                parser = Lark.open(
                    f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
                    lexer="basic",
                    priority="invert",
                    parser="earley",
                    start="file",
                    maybe_placeholders=False,
                    propagate_positions=True,
                )
            case "reti":
                parser = Lark.open(
                    f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_reti.lark",
                    lexer="basic",
                    priority="invert",
                    parser="earley",
                    start="program",
                    maybe_placeholders=False,
                    propagate_positions=True,
                )
            case _:
                print("Error: No such extension")
                exit(1)

        tokens = list(parser.lex(self.code_with_file))

        # find token with same position
        for i, token in enumerate(tokens):
            # -1 because Lark starts counting from 1
            if token.line - 1 == pos.line and token.column - 1 == pos.column:
                break
        return tokens[i - 1]

    def _find_last_token(self) -> Token:
        match global_vars.args.extension:
            case "picoc":
                parser = Lark.open(
                    f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
                    lexer="basic",
                    priority="invert",
                    parser="earley",
                    start="file",
                    maybe_placeholders=False,
                    propagate_positions=True,
                )
            case "reti":
                parser = Lark.open(
                    f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_reti.lark",
                    lexer="basic",
                    priority="invert",
                    parser="earley",
                    start="program",
                    maybe_placeholders=False,
                    propagate_positions=True,
                )
            case _:
                print("Error: No such extension")
                exit(1)

        tokens = list(parser.lex(self.code_with_file))
        return tokens[-1]

    def _output_error(self, error_str, error_name):
        print(error_str)
        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".output", "w", encoding="utf-8"
            ) as fout:
                fout.write(error_name + " ")
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
            self.screen[3 * rel_row + 1],
            "~" * width,
            pos.column + self.color_offset,
            CM().BLUE,
        )
        self.marked_lines += [3 * rel_row + 1]

    def mark_consider_colors(self, pos: Pos, width: int):
        rel_row = pos.line - self.row_from

        len_line_before = len(self.screen[3 * rel_row + 1])

        self.screen[3 * rel_row + 1] = overwrite(
            self.screen[3 * rel_row + 1], "~" * width, pos.column, CM().BLUE
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
        self.screen[rel_line * 3 + 1] = " " * (len(self.screen[rel_line * 3 + 1]) + 1)

    def __repr__(self):
        acc = "\n"

        for line in self.context_above + self.screen + self.context_below:
            acc += line + "\n"

        return acc[:-1]
