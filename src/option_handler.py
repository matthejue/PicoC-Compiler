from sre_constants import FAILURE, SUCCESS
from src import global_vars
from src import symbol_table as st
from src import picoc_nodes as pn
from src import reti_nodes as rn
import sys
import shutil
from lark.lark import Lark
from src.dt_visitors import (
    DTVisitorPicoC,
    DTSimpleVisitorPicoC,
)
from src.ast_transformers import TransformerPicoC, ASTTransformerRETI
from src.passes import Passes
from src.utils.util_funs_dependent import remove_ext, throw_type_error, subheading, get_ext
import subprocess, os, platform
from pygments.lexers.c_cpp import CLexer
import re
import argparse
from src.preprocessor import Preprocessor
from typing import Iterable, List, Optional, Dict, Any, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import traceback
from typing import cast


class OptionHandler:
    def __init__(self):
        _set_terminal_size()
        _parse_cli_args()
        _print_args_if_verbose()
        if not global_vars.args.infiles and sys.stdin.isatty():
            open_documentation()

    def build_all(self, max_workers=None):
        files = list(global_vars.args.infiles)  # strings, as passed on CLI
        if not files:
            return

        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="builder") as ex:
            fut_for = {ex.submit(self.build_file, f): f for f in files}
            for fut in as_completed(fut_for):
                f = fut_for[fut]
                try:
                    fut.result()
                except Exception as e:
                    print(f"[ERROR] {f}: {e}")
                    if global_vars.args.traceback:
                        traceback.print_exc()
                    exit(FAILURE)


    def build_file(self, path: str):
        global_vars.tstate.path_without_ext = remove_ext(path)

        extension = get_ext(path)  # still a string
        match extension:
            case "picoc":
                _syntax_check([path])                 # use the actual file string
                preprocessed_code = self._preprocess(path)
                preprocessed_code_with_filename = (
                    (
                        "./"
                        if not path.startswith("./")
                        and not path.startswith("/")
                        else ""
                    )
                    + f"{path}\n"
                    + preprocessed_code
                )
                self._compl(preprocessed_code_with_filename)
            case "reti_blocks":
                # convert reti_blocks to ast
                # lock for .json_file
                # convert datatype to string with build_ast_from_string
                pass
            case _:
                print(f"filename: {path}")
                print(f"File with extension '.{extension}' is not supported")

    def _preprocess(self, path):
        with open(path, encoding="utf-8") as fin:
            code = fin.read()

        _get_test_metadata(code)

        if global_vars.args.intermediate_stages:
            print(subheading("Raw Code", "-"))
            print(code)

        preprocessor = Preprocessor(
            include_paths=global_vars.args.I, max_depth=global_vars.args.max_depth
        )
        return preprocessor.preprocess(code, path)

    def _compl(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        if global_vars.args.intermediate_stages:
            print(subheading("Preprocessed Code", "-"))
            print(code)

        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/src/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            # propagate_positions=True,
        )

        self._tokens_option(code, "Tokens")
        dt = parser.parse(code)

        dt_visitor_picoc = DTVisitorPicoC()
        dt_visitor_picoc.visit(dt)

        self._dt_pass(dt, "Derivation Tree")

        dt_simple_visitor_picoc = DTSimpleVisitorPicoC()
        dt_simple_visitor_picoc.visit(dt)

        self._dt_pass(dt, "Derivation Tree Simple")

        ast_transformer_picoc = TransformerPicoC()
        ast = ast_transformer_picoc.transform(dt)

        self._output_pass(ast, "Abstract Syntax Tree")
        passes = Passes()

        picoc_shrink = passes.picoc_shrink(ast)
        self._output_pass(picoc_shrink, "PicoC Shrink")

        picoc_blocks = passes.picoc_blocks(picoc_shrink)
        self._output_pass(picoc_blocks, "PicoC Blocks")

        picoc_anf = passes.picoc_anf(picoc_blocks)
        self._output_pass(picoc_anf, "PicoC ANF")
        self._st_pass(passes.symbol_table, "Symbol Table")

        reti_blocks = passes.reti_blocks(picoc_anf)
        self._output_pass(reti_blocks, "RETI Blocks")

        reti_patch = passes.reti_patch(reti_blocks)
        self._output_pass(reti_patch, "RETI Patch")

        reti = passes.reti(reti_patch)

        self._reti_with_metadata(reti, "RETI")

    def _tokens_option(self, code_with_file, heading):
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/src/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            # propagate_positions=True,
        )
        tokens = list(parser.lex(code_with_file))

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(tokens)

        if global_vars.args.write_files:
            with open(
                global_vars.tstate.path_without_ext
                + ".tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(tokens))

    def _dt_pass(self, dt, heading):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(dt.pretty().replace("\t", "    "))

        if global_vars.args.write_files:
            with open(dt.children[0].value, "w", encoding="utf-8") as fout:
                fout.write(dt.pretty())

    def _output_pass(self, pass_ast, heading):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(pass_ast)

        if global_vars.args.write_files:
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

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(metadata + str(pass_ast))

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
        at_least_one_file = len(global_vars.args.infiles) > 1
        if global_vars.args.intermediate_stages or at_least_one_file:
            json_symbol_table = symbol_table.to_json_str(pretty=True)

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(json_symbol_table)

        if at_least_one_file:
            with open(
                global_vars.tstate.path_without_ext + ".json",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(json_symbol_table))

def _parse_cli_args():
    parser = argparse.ArgumentParser(
        prog="picoc-compiler",
        description="Plain CLI tool — no shell. Processes an input file with flags.",
    )
    parser.add_argument(
        "infiles",
        nargs="+",
        help="Path(s) to input file(s), or '-' for stdin",
    )
    parser.add_argument(
        "-i",
        "--intermediate_stages",
        action="store_true",
        help="Emit or keep intermediate stages",
    )
    parser.add_argument(
        "-w",
        "--write_files",
        dest="write_files",
        action="store_true",
        help="Write output to files",
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
    from src.global_vars import args  # uses the shared args object

    if not getattr(args, "verbose", False):
        return  # quiet unless -v/--verbose is on

    def kind(name, value):
        if name == "infiles":
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
        "infiles",
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


def open_documentation():
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
        if os.path.isfile(global_vars.tstate.path_without_ext + ".in"):
            with open(
                global_vars.tstate.path_without_ext + ".in", "r", encoding="utf-8"
            ) as fin:
                global_vars.input = [
                    int(line)
                    for line in fin.readline().replace("\n", "").split(" ")
                    if line.lstrip("-").isdigit()
                ]


def _syntax_check(
    c_files: "Iterable[str]",
    extra_flags: "Optional[Sequence[str]]" = None,
    compiler: "Optional[str]" = None,
    timeout: int = 60,
) -> None:
    if global_vars.args.supress_errors:
        return
    c_files_list: List[str] = list(c_files)
    if not c_files_list:
        print("syntax_check: no C files provided", file=sys.stderr)
        os._exit(2)

    chosen = compiler or shutil.which("clang") or shutil.which("gcc")
    if not chosen:
        print(
            "syntax_check: no suitable C compiler found (need clang or gcc)",
            file=sys.stderr,
        )
        os._exit(2)

    flags: List[str] = [
        "-x",
        "c",
        "-fsyntax-only",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-std=c11",
    ]
    if extra_flags:
        flags.extend(list(extra_flags))

    cmd: List[str] = [chosen] + flags + c_files_list
    try:
        # Inherit stdout/stderr so compiler diagnostics stream to your terminal immediately.
        p: subprocess.CompletedProcess[int] = subprocess.run(cmd, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"syntax_check: compiler timed out after {timeout}s", file=sys.stderr)
        os._exit(124)

    if p.returncode != 0:
        # Diagnostics already printed by the compiler; exit the whole program.
        os._exit(p.returncode)
