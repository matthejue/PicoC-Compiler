import global_vars
import symbol_table as st
import picoc_nodes as pn
import reti_nodes as rn
import sys
import shutil
from lark.lark import Lark
from dt_visitors import (
    DTVisitorPicoC,
    DTSimpleVisitorPicoC,
)
from ast_transformers import TransformerPicoC, ASTTransformerRETI
from passes import Passes
from util_funs import remove_extension, throw_type_error, subheading, get_extension
import subprocess, os, platform
from pygments.lexers.c_cpp import CLexer
import re
import argparse
from preprocessor import Preprocessor


class OptionHandler:
    def __init__(self):
        _set_terminal_size()
        _parse_cli_args()
        _print_args_if_verbose()
        if not global_vars.args.infile and sys.stdin.isatty():
            _open_documentation()

    def read_and_write_file(self):
        with open(global_vars.args.infile, encoding="utf-8") as fin:
            code = fin.read()

        global_vars.args.extension = get_extension(global_vars.args.infile)
        match global_vars.args.extension:
            case "picoc":
                self._compl(code)
            case _:
                print("filename: " + global_vars.args.infile)
                print(
                    f"File with extension '.{global_vars.args.extension}' cannot be compiled or interpreted."
                )

    def _compl(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        _get_test_metadata(code)

        preprocessor = Preprocessor(include_paths=global_vars.args.I, max_depth=global_vars.args.max_depth)
        preprocessed_code = preprocessor.preprocess(code, global_vars.args.infile)

        code_with_file = (
            (
                "./"
                if not global_vars.args.infile.startswith("./")
                and not global_vars.args.infile.startswith("/")
                else ""
            )
            + f"{global_vars.args.infile}\n"
            + preprocessed_code
        )

        if global_vars.args.intermediate_stages and global_vars.args.print:
            print(subheading("Code", "-"))
            print(code_with_file)

        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            # propagate_positions=True,
        )

        if global_vars.args.intermediate_stages:
            self._tokens_option(code_with_file, "Tokens", "picoc")

        dt = parser.parse(code_with_file)

        dt_visitor_picoc = DTVisitorPicoC()
        dt_visitor_picoc.visit(dt)

        if global_vars.args.intermediate_stages:
            self._dt_pass(dt, "Derivation Tree")

        dt_simple_visitor_picoc = DTSimpleVisitorPicoC()
        dt_simple_visitor_picoc.visit(dt)

        if global_vars.args.intermediate_stages:
            self._dt_pass(dt, "Derivation Tree Simple")

        ast_transformer_picoc = TransformerPicoC()
        ast = ast_transformer_picoc.transform(dt)

        if global_vars.args.intermediate_stages:
            self._output_pass(ast, "Abstract Syntax Tree")

        passes = Passes()

        picoc_shrink = passes.picoc_shrink(ast)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_shrink, "PicoC Shrink")

        picoc_blocks = passes.picoc_blocks(picoc_shrink)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_blocks, "PicoC Blocks")

        picoc_anf = passes.picoc_anf(picoc_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_anf, "PicoC ANF")

        if global_vars.args.intermediate_stages:
            self._st_pass(passes.symbol_table, "Symbol Table")

        reti_blocks = passes.reti_blocks(picoc_anf)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_blocks, "RETI Blocks")

        reti_patch = passes.reti_patch(reti_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_patch, "RETI Patch")

        reti = passes.reti(reti_patch)

        self._reti_with_metadata(reti, "RETI")

    def _tokens_option(self, code_with_file, heading, picoc_or_reti):
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_{picoc_or_reti}.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file" if picoc_or_reti == "picoc" else "program",
            maybe_placeholders=False,
            # propagate_positions=True,
        )
        tokens = list(parser.lex(code_with_file))

        if global_vars.args.print:
            print(subheading(heading, "-"))
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
            print(subheading(heading, "-"))
            print(dt.pretty().replace("\t", "    "))

        if global_vars.path:
            with open(dt.children[0].value, "w", encoding="utf-8") as fout:
                fout.write(dt.pretty())

    def _output_pass(self, pass_ast, heading):
        if global_vars.args.print:
            print(subheading(heading, "-"))
            print(pass_ast)

        match pass_ast:
            case pn.File(pn.Name(val)):
                with open(val, "w", encoding="utf-8") as fout:
                    fout.write(str(pass_ast))
            case rn.Program(rn.Name(val)):
                with open(val, "w", encoding="utf-8") as fout:
                    fout.write(str(pass_ast))
            case _:
                throw_type_error(pass_ast)

    def _reti_with_metadata(self, pass_ast, heading):
        metadata = f"# input: {' '.join(map(lambda x: str(x), global_vars.input))}\n# expected: {' '.join(map(lambda x: str(x), global_vars.expected))}\n"

        if global_vars.args.print:
            print(subheading(heading, "-"))
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
                    throw_type_error(pass_ast)

    def _st_pass(self, symbol_table: st.SymbolTable, heading):
        if global_vars.args.print:
            print(subheading(heading, "-"))
            print(symbol_table)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".st",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(symbol_table))


def _parse_cli_args():
    parser = argparse.ArgumentParser(
        prog="picoc-compiler",
        description="Plain CLI tool — no shell. Processes an input file with flags.",
    )
    parser.add_argument("infile", nargs="?", help="Path to the input file")

    parser.add_argument(
        "-i",
        "--intermediate_stages",
        action="store_true",
        help="Emit or keep intermediate stages",
    )
    parser.add_argument(
        "-p",
        "--print",
        dest="print",
        action="store_true",
        help="Print output to stdout",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Create comments for immediate stages",
    )
    parser.add_argument(
        "-vv",
        "--double_verbose",
        action="store_true",
        help="Additionaly makes formatting wider",  # and adds datatype to ref and adds BuiltinTypes char and int to SymbolTable"
    )
    parser.add_argument("-e", "--example", action="store_true", help="Run example mode")
    parser.add_argument(
        "-t",
        "--traceback",
        action="store_true",
        help="Show full tracebacks on errors",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "-s",
        "--supress_errors",
        action="store_true",
        help="Suppress non-critical errors",
    )  # kept original spelling
    parser.add_argument(
        "-b", "--binary", action="store_true", help="Produce binary output"
    )
    parser.add_argument(
        "-n", "--no_long_jumps", action="store_true", help="Disable long jumps"
    )
    parser.add_argument(
        "-m",
        "--metadata_comments",
        action="store_true",
        help="Include metadata comments",
    )
    # ------------------------------- Preprocessor ----------------------------
    parser.add_argument(
        "-I", dest="I", action="append", default=[], help="include path (repeatable)"
    )
    parser.add_argument("--max-depth", type=int, default=200, help="max include depth")

    global_vars.args = parser.parse_args()


def _set_terminal_size():
    size = shutil.get_terminal_size(fallback=(72, 24))
    if sys.stdin.isatty():
        global_vars.terminal_columns, global_vars.terminal_lines = (
            size.columns,
            size.lines,
        )


def _print_args_if_verbose():
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
        "traceback",
        "debug",
        "supress_errors",
        "binary",
        "no_long_jumps",
        "metadata_comments",
    ]

    print(subheading("CLI options", "-"))
    for name in fields:
        value = getattr(args, name, None)
        print(f"{name:20} [{kind(name, value):10}] = {fmt(value)}")


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
    else:
        if os.path.isfile(global_vars.path + global_vars.basename + ".in"):
            with open(
                global_vars.path + global_vars.basename + ".in", "r", encoding="utf-8"
            ) as fin:
                global_vars.input = [
                    int(line)
                    for line in fin.readline().replace("\n", "").split(" ")
                    if line.lstrip("-").isdigit()
                ]
