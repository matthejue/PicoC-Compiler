import global_vars
import cmd2
from error_handler import ErrorHandler
import symbol_table as st
import picoc_nodes as pn
import reti_nodes as rn
import sys
from lark.lark import Lark
from dt_visitors import (
    DTVisitorPicoC,
    DTSimpleVisitorPicoC,
    DTVisitorRETI,
)
from ast_transformers import TransformerPicoC, ASTTransformerRETI
from passes import Passes
from util_funs import remove_extension, subheading, throw_error, get_extension
import subprocess, os, platform
from pygments.lexers.c_cpp import CLexer
import re


class OptionHandler(cmd2.Cmd):
    cli_args_parser = cmd2.Cmd2ArgumentParser(add_help=False)
    cli_args_parser.add_argument("infile", nargs="?")
    cli_args_parser.add_argument("-i", "--intermediate_stages", action="store_true")
    cli_args_parser.add_argument("-p", "--print", action="store_true")
    cli_args_parser.add_argument("-v", "--verbose", action="store_true")
    cli_args_parser.add_argument("-vv", "--double_verbose", action="store_true")
    cli_args_parser.add_argument("-l", "--lines", type=int, default=2)
    cli_args_parser.add_argument("-e", "--example", action="store_true")
    cli_args_parser.add_argument("-t", "--traceback", action="store_true")
    cli_args_parser.add_argument("-d", "--debug", action="store_true")
    cli_args_parser.add_argument("-s", "--supress_errors", action="store_true")
    cli_args_parser.add_argument("-b", "--binary", action="store_true")
    cli_args_parser.add_argument("-n", "--no_long_jumps", action="store_true")
    cli_args_parser.add_argument("-m", "--metadata_comments", action="store_true")

    HISTORY_FILE = os.path.expanduser("~") + "/.config/picoc_compiler/history.json"
    PERSISTENT_HISTORY_LENGTH = 100

    def __init__(self):
        self.terminal_columns = (
            os.get_terminal_size().columns if sys.stdin.isatty() else 72
        )
        self.terminal_lines = os.get_terminal_size().lines if sys.stdin.isatty() else 24
        global_vars.args = self.cli_args_parser.parse_args()
        self.print_args_if_verbose()
        if not global_vars.args.infile and sys.stdin.isatty():
            self._shell__init__()

    def print_args_if_verbose(self):
        from global_vars import args  # uses the shared args object

        if not getattr(args, "verbose", False):
            return  # quiet unless -v/--verbose is on

        def kind(name, value):
            if name == "infile":
                return "positional"
            if isinstance(value, bool):
                return "flag"
            if isinstance(value, int):
                return "int"
            return "str"

        def fmt(value):
            if isinstance(value, bool):
                return "ON" if value else "off"
            if value is None:
                return "(none)"
            return str(value)

        fields = [
            "infile",
            "intermediate_stages",
            "print",
            "verbose",
            "double_verbose",
            "lines",
            "color",
            "traceback",
            "debug",
            "supress_errors",
            "binary",
            "no_long_jumps",
            "metadata_comments",
        ]

        print("=== CLI options ===")
        for name in fields:
            value = getattr(args, name, None)
            print(f"{name:20} [{kind(name, value):10}] = {fmt(value)}")

    def _shell__init__(self):
        super().__init__()

        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update(
            {
                "cpl": "compile",
                "mu": "most_used",
                "itp": "interpret",
                "ct": "color_toggle",
                "cs": "compile_show",
                "is": "interpret_show",
            }
        )
        cmd2.Cmd.__init__(
            self,
            shortcuts=shortcuts,
            multiline_commands=[
                "compile",
                "most_used",
                "interpret",
                "compile_show",
                "interpret_show",
            ],
        )
        del cmd2.Cmd.do_help

        # save history hook
        self.register_postcmd_hook(self.save_history)

        self._deal_with_history_and_color_settings()

        self.prompt_and_intro()

    def _deal_with_history_and_color_settings(self):
        # load history
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE) as fin:
                self.history = self.history.from_json(fin.read())

    def save_history(
        self, _: cmd2.plugin.PostcommandData
    ) -> cmd2.plugin.PostcommandData:
        while len(self.history) > self.PERSISTENT_HISTORY_LENGTH:
            del self.history[0]
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as fout:
                fout.write(self.history.to_json())
        return _

    def prompt_and_intro(self):
        # prompts
        self.prompt = "PicoC> "
        self.continuation_prompt = "> "

        # intro
        self.intro = "PicoC Shell ready. Enter `help` (shortcut `?`) to see the manual."

    @cmd2.with_argparser(cli_args_parser)
    def do_compile(self, args):
        code = args.infile
        color = global_vars.args.color
        global_vars.args = args
        global_vars.args.infile = "term.picoc"
        global_vars.args.color = color
        global_vars.args.print = True
        global_vars.args.extension = "picoc"
        self._compl("void main() {" + code + "}")
        print(f"\nCompilation successfull\n")

    @cmd2.with_argparser(cli_args_parser)
    def do_most_used(self, args):
        code = args.infile
        color = global_vars.args.color
        global_vars.args = global_vars.Args()
        global_vars.args.color = color
        global_vars.args.print = True
        global_vars.args.extension = "picoc"
        self._compl("void main() {" + code + "}")
        print(
            f"\nCompilation and Interpretation successfull\n"
        )

    @cmd2.with_argparser(cli_args_parser)
    def do_interpret(self, args):
        code = args.infile
        color = global_vars.args.color
        global_vars.args = args
        global_vars.args.infile = "term.reti"
        global_vars.args.color = color
        global_vars.args.print = True
        global_vars.args.extension = "reti"
        self._interp(code)
        print(
            f"\nInterpretation successfull\n"
        )

    def do_help(self, _):
        _open_documentation()

    def read_and_write_file(self):
        with open(global_vars.args.infile, encoding="utf-8") as fin:
            code = fin.read()

        global_vars.args.extension = get_extension(global_vars.args.infile)
        match global_vars.args.extension:
            case "picoc":
                self._compl(code)
            case "reti":
                self._interp(code)
            case _:
                print("filename: " + global_vars.args.infile)
                print(
                    f"File with extension '.{global_vars.args.extension}' cannot be compiled or interpreted."
                )

    def read_stdin(self):
        if global_vars.args.plugin_support:
            global_vars.args.metadata_comments = True
            code = input()
            code = code.replace(chr(30), "\n")
        else:
            code = sys.stdin.read()
        if not global_vars.args.extension:
            print("Need extension option set if passing code via stdin.")
            exit(1)
        match global_vars.args.extension:
            case "picoc":
                global_vars.args.infile = "stdin.picoc"
                self._compl(code)
            case "reti":
                global_vars.args.infile = "stdin.reti"
                self._interp(code)
            case _:
                print("filename: " + global_vars.args.infile)
                print(
                    f"File with extension '.{global_vars.args.extension}' cannot be compiled or interpreted."
                )
        self._success_message()

    def _compl(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        code_with_file = (
            (
                "./"
                if not global_vars.args.infile.startswith("./")
                and not global_vars.args.infile.startswith("/")
                else ""
            )
            + f"{global_vars.args.infile}\n"
            + code
        )

        _get_test_metadata(code)

        if global_vars.args.intermediate_stages and global_vars.args.print:
            print(subheading("Code", self.terminal_columns, "-"))
            inserted_code = f"// {global_vars.args.infile}:\n" + code
            if global_vars.args.color:
                print(highlight(inserted_code, CLexer(), TerminalFormatter()))
            else:
                print(inserted_code)

        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )

        # handle errors
        error_handler = ErrorHandler(code_with_file)

        if global_vars.args.intermediate_stages:
            error_handler.handle(self._tokens_option, code_with_file, "Tokens", "picoc")

        dt = error_handler.handle(parser.parse, code_with_file)

        dt_visitor_picoc = DTVisitorPicoC()
        error_handler.handle(dt_visitor_picoc.visit, dt)

        if global_vars.args.intermediate_stages:
            self._dt_pass(dt, "Derivation Tree")

        dt_simple_visitor_picoc = DTSimpleVisitorPicoC()
        error_handler.handle(dt_simple_visitor_picoc.visit, dt)

        if global_vars.args.intermediate_stages:
            self._dt_pass(dt, "Derivation Tree Simple")

        ast_transformer_picoc = TransformerPicoC()
        ast = error_handler.handle(ast_transformer_picoc.transform, dt)

        if global_vars.args.intermediate_stages:
            self._output_pass(ast, "Abstract Syntax Tree")

        passes = Passes()

        picoc_shrink = error_handler.handle(passes.picoc_shrink, ast)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_shrink, "PicoC Shrink")

        picoc_blocks = error_handler.handle(passes.picoc_blocks, picoc_shrink)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_blocks, "PicoC Blocks")

        picoc_mon = error_handler.handle(passes.picoc_anf, picoc_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_mon, "PicoC ANF")

        if global_vars.args.intermediate_stages:
            self._st_pass(passes.symbol_table, "Symbol Table")

        reti_blocks = error_handler.handle(passes.reti_blocks, picoc_mon)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_blocks, "RETI Blocks")

        reti_patch = error_handler.handle(passes.reti_patch, reti_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_patch, "RETI Patch")

        reti = error_handler.handle(passes.reti, reti_patch)

        # self._output_pass(reti, "RETI")

        self._reti_with_metadata(reti, "RETI")

        if global_vars.args.intermediate_stages:
            reti_interp = RETIInterpreter(reti)
            self._eprom_write_startprogram_to_file(reti_interp, "EPROM")

        if global_vars.args.run:
            if global_vars.args.print:
                print(subheading("RETI Run", self.terminal_columns, "-"))
            reti_interp = RETIInterpreter(reti)
            # possibility to supress error
            try:
                error_handler.handle(reti_interp.interp_reti)
            except Exception as e:
                if not global_vars.args.supress_errors:
                    raise e

    def _interp(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        code_with_file = (
            (
                "./"
                if not global_vars.args.infile.startswith("./")
                and not global_vars.args.infile.startswith("/")
                else ""
            )
            + f"{global_vars.args.infile}\n"
            + code
        )

        _get_test_metadata(code)

        if global_vars.args.intermediate_stages and global_vars.args.print:
            print(subheading("Code", self.terminal_columns, "-"))
            inserted_code = f"# {global_vars.args.infile}:\n" + code + "\n"
            if global_vars.args.color:
                print(
                    highlight(
                        inserted_code,
                        RETILexer(),
                        TerminalFormatter(
                            colorscheme={
                                Comment: ("magenta", "brightmagenta"),
                                Whitespace: ("gray", "white"),
                                Keyword: ("blue", "brightblue"),
                                Punctuation: ("gray", "white"),
                                Name: ("cyan", "brightcyan"),
                                Number: ("red", "brightred"),
                                Name.Tag: ("green", "brightgreen"),
                                Operator: ("yellow", "brightyellow"),
                            }
                        ),
                    )
                )
            else:
                print(inserted_code)

        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_reti.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="program",
            maybe_placeholders=False,
            propagate_positions=True,
        )

        # handle errors
        error_handler = ErrorHandler(code_with_file)

        if global_vars.args.intermediate_stages:
            error_handler.handle(
                self._tokens_option, code_with_file, "RETI Tokens", "reti"
            )

        # just for finding UnexpectedCharacters errors
        self._find_unexpected_characters_errors(error_handler, code_with_file)

        dt = error_handler.handle(parser.parse, code_with_file)

        dt_visitor_reti = DTVisitorRETI()
        error_handler.handle(dt_visitor_reti.visit, dt)

        if global_vars.args.intermediate_stages:
            self._dt_pass(dt, "RETI Derivation Tree")

        ast_transformer_reti = ASTTransformerRETI()
        ast = error_handler.handle(ast_transformer_reti.transform, dt)

        if global_vars.args.intermediate_stages:
            self._output_pass(ast, "RETI Abstract Syntax Tree")

        if global_vars.args.print:
            print(subheading("RETI Run", self.terminal_columns, "-"))

        reti_interp = RETIInterpreter(ast)

        # possibility to supress error
        try:
            error_handler.handle(reti_interp.interp_reti)
        except Exception as e:
            if not global_vars.args.supress_errors:
                raise e

    def _success_message(self):
        if global_vars.args.plugin_support:
            return
        if global_vars.args.run:
            match global_vars.args.extension:
                case "reti":
                    print(
                        f"\nInterpretation successfull\n"
                    )
                case _:
                    print(
                        f"\nCompilation and Interpretation successfull\n"
                    )
        else:
            match global_vars.args.extension:
                case "picoc":
                    print(
                        f"\nCompilation successfull\n"
                    )
                case "reti":
                    print(
                        f"\nInterpretation successfull\n"
                    )

    def _tokens_option(self, code_with_file, heading, picoc_or_reti):
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_{picoc_or_reti}.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file" if picoc_or_reti == "picoc" else "program",
            maybe_placeholders=False,
            propagate_positions=True,
        )
        tokens = list(parser.lex(code_with_file))

        if global_vars.args.print:
            print(subheading(heading, self.terminal_columns, "-"))
            if global_vars.args.color:
                print(
                    highlight(
                        str(tokens),
                        TokenLexer(),
                        TerminalFormatter(
                            colorscheme={
                                Whitespace: ("gray", "white"),
                                Keyword: ("blue", "brightblue"),
                                Punctuation: ("gray", "white"),
                                String.Delimiter: ("cyan", "brightcyan"),
                                Name.Variable: ("green", "brightgreen"),
                                Name.Attribute: ("red", "brightred"),
                            }
                        ),
                    )
                )
            else:
                print(tokens)

        if global_vars.path:
            with open(
                remove_extension(tokens[0].value)
                + f".{'r' if picoc_or_reti == 'reti' else ''}tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(tokens))

    def _dt_pass(self, dt, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_columns, "-"))
            if global_vars.args.color:
                print(
                    highlight(
                        dt.pretty().replace("\t", "    "),
                        DTLexer(),
                        TerminalFormatter(
                            colorscheme={
                                Whitespace: ("gray", "white"),
                                Name.Variable: ("blue", "brightgreen"),
                                Name.Attribute: ("red", "brightred"),
                            }
                        ),
                    )
                )
            else:
                print(dt.pretty().replace("\t", "    "))

        if global_vars.path:
            with open(dt.children[0].value, "w", encoding="utf-8") as fout:
                fout.write(dt.pretty())

    def _output_pass(self, pass_ast, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_columns, "-"))
            print(pass_ast)

        if global_vars.path:
            match pass_ast:
                case pn.File(pn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(pass_ast))
                case rn.Program(rn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(pass_ast))
                case _:
                    throw_error(pass_ast)

    def _reti_with_metadata(self, pass_ast, heading):
        metadata = f"# input: {' '.join(map(lambda x: str(x), global_vars.input))}\n# expected: {' '.join(map(lambda x: str(x), global_vars.expected))}\n# datasegment: {global_vars.datasegment}\n"

        if global_vars.args.print:
            print(subheading(heading, self.terminal_columns, "-"))
            print(metadata + str(pass_ast))

        if global_vars.path:
            match pass_ast:
                case rn.Program(rn.Name(val)):
                    # insert at the beginning of the file
                    with open(
                        val,
                        "w",
                        encoding="utf-8",
                    ) as fout:
                        fout.write(metadata + str(pass_ast))
                case _:
                    throw_error(pass_ast)

    def _st_pass(self, symbol_table: st.SymbolTable, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_columns, "-"))
            print(symbol_table)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".st",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(symbol_table))

    def _eprom_write_startprogram_to_file(self, reti_interp: RETIInterpreter, heading):
        if global_vars.args.print:
            acc = ""
            for cell in reti_interp.reti.eprom.cells.values():
                acc += str(cell)
            print(subheading(heading, self.terminal_columns, "-"))
            print(acc.lstrip())

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".eprom",
                "w",
                encoding="utf-8",
            ) as fout:
                acc = ""
                for cell in reti_interp.reti.eprom.cells.values():
                    acc += str(cell)

                fout.write(acc.lstrip())

    def _find_unexpected_characters_errors(self, error_handler, code_with_file):
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

        error_handler.handle(list, parser.lex(code_with_file))


def _open_documentation():
    filepath = os.path.dirname(os.path.realpath(sys.argv[0])) + "/Dokumentation.pdf"

    #  https://stackoverflow.com/questions/7343388/open-pdf-with-default-program-in-windows-7
    # https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", filepath))
    elif platform.system() == "Windows":  # Windows
        os.startfile(filepath)
    elif platform.system() == "Linux":  # linux variants
        subprocess.call(("xdg-open", filepath))
    else:
        print("OS not supported.")


def _get_test_metadata(code):
    if global_vars.args.metadata_comments:
        regex = re.search(
            r"((\/\/|#) +in(put)?: *([\d\-]+( +[\d\-]+)*)? *\n)?((\/\/|#) +exp(ected)?: *([\d\-]+( +[\d\-]+)*)? *\n)?((\/\/|#) +data(segment)?: *([\d\-]+)? *\n)?",
            code,
        )
        if regex:
            global_vars.input = (
                list(map(lambda x: int(x), regex.group(4).split()))
                if regex.group(4)
                else []
            )
            global_vars.expected = (
                list(map(lambda x: int(x), regex.group(9).split()))
                if regex.group(9)
                else []
            )
            if global_vars.args.datasegment_size:  # defaults to 0
                global_vars.datasegment = global_vars.args.datasegment_size
            else:
                global_vars.datasegment = (
                    int(regex.group(14)) if regex.group(14) else 64
                )
    else:
        if global_vars.args.datasegment_size:  # defaults to 0
            global_vars.datasegment = global_vars.args.datasegment_size
        elif os.path.isfile(
            global_vars.path + global_vars.basename + ".datasegment_size"
        ):
            with open(
                global_vars.path + global_vars.basename + ".datasegment_size",
                "r",
                encoding="utf-8",
            ) as fin:
                global_vars.datasegment = int(fin.read())

        if os.path.isfile(global_vars.path + global_vars.basename + ".in"):
            with open(
                global_vars.path + global_vars.basename + ".in", "r", encoding="utf-8"
            ) as fin:
                global_vars.input = [
                    int(line)
                    for line in fin.readline().replace("\n", "").split(" ")
                    if line.lstrip("-").isdigit()
                ]
