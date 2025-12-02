from sre_constants import FAILURE, SUCCESS
from src import global_vars
from src import symbol_table as st
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src import debug as db
import sys
import shutil
from lark.lark import Lark
from src.ast_node import ASTNode
from src.dt_visitors import (
    DTVisitorPicoC,
    DTSimpleVisitorPicoC,
)
from src.ast_transformers import TransformerPicoC, ASTTransformerRETI
from src.passes import Passes
from src.utils.util_funs_dependent import (
    remove_ext,
    throw_error,
    subheading,
    get_ext,
)
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
        _install_post_mortem_hook()
        _print_args_if_verbose()
        if not global_vars.args.infiles and sys.stdin.isatty():
            open_documentation()

    def build_all(self, max_workers=None):
        files = list(global_vars.args.infiles)  # strings, as passed on CLI
        _syntax_check(files)
        if not files:
            return

        results = []

        if global_vars.args.intermediate_stages:
            for f in files:
                try:
                    result = self.build_file(f)
                    results.append(result)  # store filename + return value
                except Exception as e:
                    if global_vars.args.debug:
                        raise  # let the post-mortem hook handle it
                    print(f"[ERROR] {f}: {e}")
                    if global_vars.args.traceback:
                        traceback.print_exc()
                    exit(FAILURE)
        else:
            with ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="builder"
            ) as ex:
                fut_for = {ex.submit(self.build_file, f): f for f in files}
                for fut in as_completed(fut_for):
                    f = fut_for[fut]
                    try:
                        result = fut.result()
                        results.append(result)
                    except Exception as e:
                        if global_vars.args.debug:
                            raise  # let the post-mortem hook handle it
                        print(f"[ERROR] {f}: {e}")
                        if global_vars.args.traceback:
                            traceback.print_exc()
                        exit(FAILURE)

        asts, symbol_tables, all_file_blocks = (
            map(list, zip(*results)) if results else ([], [], [])
        )

        _get_test_metadata()

        if not global_vars.args.compile:
            self._insert_start_fun(asts, symbol_tables, all_file_blocks)
            self._link(asts, symbol_tables, all_file_blocks)

    def build_file(self, path: str):
        global_vars.tstate.path_without_ext = remove_ext(path)

        extension = get_ext(path)  # still a string
        match extension:
            case "picoc":
                preprocessed_code = self._preprocess(path)
                preprocessed_code_with_filename = (
                    (
                        "./"
                        if not path.startswith("./") and not path.startswith("/")
                        else ""
                    )
                    + f"{path}\n"
                    + preprocessed_code
                )
                return self._compl(preprocessed_code_with_filename)
            case "reti_blocks":
                # convert reti_blocks to ast
                # lock for .json_file
                # convert datatype to string with build_ast_from_string
                pass
            case _:
                print(f"filename: {path}")
                print(f"File with extension '.{extension}' is not supported")
                exit(FAILURE)

    def _preprocess(self, path):
        with open(path, encoding="utf-8") as fin:
            code = fin.read()

        if global_vars.args.intermediate_stages:
            print(subheading("Raw Code", "-"))
            print(code)

        preprocessor = Preprocessor(
            include_paths=global_vars.args.I, max_depth=global_vars.args.max_depth
        )
        return preprocessor.preprocess(code, path)

    def _compl(self, code):
        # db.activate_debug()
        # db.debug()

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

        db.activate_debug()
        picoc_typing = passes.picoc_typing(picoc_blocks)
        self._output_pass(picoc_typing, "PicoC Typing")

        picoc_anf = passes.picoc_anf(picoc_typing)
        self._output_pass(picoc_anf, "PicoC ANF")
        self._st_pass(
            passes.symbol_table,
            "Symbol Table",
            compl_opt_active=global_vars.args.compile,
        )

        reti_blocks = passes.reti_blocks(picoc_anf)
        self._output_pass(
            reti_blocks, "RETI Blocks", compl_opt_active=global_vars.args.compile
        )
        return reti_blocks, passes.symbol_table, passes.all_blocks

    def _link(self, asts, symbol_tables, all_file_blocks):
        merged_ast = self._merge_asts(asts)
        passes = Passes()
        passes.all_blocks = {k: v for d in all_file_blocks for k, v in d.items()}
        passes.symbol_table = self._merge_symbol_tables(symbol_tables)

        self._st_pass(passes.symbol_table, "Combined Symbol Table", is_global_st=True)

        reti_patch = passes.reti_patch(merged_ast)
        self._output_pass(
            reti_patch,
            "RETI Patch",
        )
        reti = passes.reti(reti_patch)
        self._reti_with_metadata(reti, "RETI")

    def _insert_start_fun(self, asts, symbol_tables, all_file_blocks):
        passes = Passes()
        global_inits = []

        for file_ast in asts:
            match file_ast:
                case pn.File(filename, blocks):
                    # iterate safely (copy, since we remove in place)
                    for block in blocks[:]:
                        match block:
                            case pn.Block("_global_inits", inits):
                                global_inits.extend(inits)
                                blocks.remove(block)
                            case pn.Block(_, _):
                                continue
                            case _:
                                print(
                                    f"[error] Unexpected block type in file '{filename}': {type(block).__name__}",
                                    file=sys.stderr,
                                )
                                sys.exit(FAILURE)

                case _:
                    print(
                        f"[error] Unexpected AST node (expected File), got: {type(file_ast).__name__}",
                        file=sys.stderr,
                    )
                    sys.exit(FAILURE)

        main_func = None
        for symbol_table in symbol_tables:
            if symbol_table.contains("main", scope="global"):
                main_func = symbol_table._table["global"]["main"]
                break

        if main_func is None:
            print(
                "[error] No 'main' function found in any symbol table.", file=sys.stderr
            )
            sys.exit(FAILURE)

        passes.symbol_table.declare("main", main_func, scope="global")

        start_ast = pn.File(
            pn.Name("start"),
            [
                pn.Block(
                    "_start",
                    passes._picoc_anf_stmt(pn.Exp(pn.Call(pn.Name("main"), [])))
                    + [pn.Exit(pn.Num("0"))],
                )
            ],
        )

        reti_blocks: pn.File = passes.reti_blocks(start_ast)

        reti_blocks.decls_defs_blocks_instrs[0].stmts_instrs[:0] = global_inits

        # Insert at the beginning so _start comes first
        asts.insert(0, reti_blocks)
        symbol_tables.insert(0, passes.symbol_table)
        all_file_blocks.insert(0, passes.all_blocks)

    def _merge_asts(self, asts):
        global_vars.tstate.path_without_ext = remove_ext(global_vars.args.output_name)

        if not asts:
            return pn.File(pn.Name(global_vars.args.output_name), [])

        # collect all decls_defs_blocks_instrs into one list
        merged_decls_defs_blocks_instrs = []
        for ast in asts:
            merged_decls_defs_blocks_instrs.extend(ast.decls_defs_blocks_instrs)

        # return a new merged File node
        return pn.File(pn.Name(global_vars.args.output_name), merged_decls_defs_blocks_instrs)

    def _merge_symbol_tables(self, symbol_tables):
        if not symbol_tables:
            symbol_table = st.SymbolTable()
            return symbol_table

        merged_table = {}
        merged_parents = {}

        # Merge all symbol tables
        for symbol_table in symbol_tables:
            for scope, symbols in symbol_table.items():
                if scope == "__parents__":
                    for k, v in symbols.items():
                        merged_parents[k] = v
                else:
                    merged_table.setdefault(scope, {})
                    merged_table[scope].update(symbols)

        # Ensure global scope exists
        merged_table.setdefault("global", {})
        merged_parents.setdefault("global", None)

        # Assign distinct addresses only for globals that have BOTH 'addr' and 'size'
        current_addr = 0
        for sym_name, sym in merged_table["global"].items():
            if "addr" in sym and "size" in sym:
                sym["addr"] = current_addr
                current_addr += sym["size"]

        # Build final merged SymbolTable object
        merged_st = st.SymbolTable()
        merged_st._table = merged_table
        merged_st._parents = merged_parents
        return merged_st

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
                global_vars.tstate.path_without_ext + ".tokens",
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

    def _output_pass(self, pass_ast: pn.File, heading, *, compl_opt_active=False):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(pass_ast.__repr__(incl_filenode=True)[1:])

        if global_vars.args.write_files or compl_opt_active:
            match pass_ast:
                case pn.File(pn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(pass_ast)[1:])
                case _:
                    throw_error(pass_ast)

    def _st_pass(self, symbol_table: st.SymbolTable, heading, compl_opt_active=False, is_global_st=False):
        if (
            global_vars.args.intermediate_stages
            or global_vars.args.write_files
            or compl_opt_active
        ):
            json_symbol_table = symbol_table.to_json_str(pretty=True)

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(json_symbol_table)

        if global_vars.args.write_files or compl_opt_active:
            with open(
                global_vars.tstate.path_without_ext + ".json",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(json_symbol_table))

    def _reti_with_metadata(self, pass_ast: pn.File, heading):
        pass_ast.decls_defs_blocks_instrs[:0] = [
            pn.SingleLineComment(
                "#", f"input: {' '.join(map(lambda x: str(x), global_vars.input))}"
            ),
            pn.SingleLineComment(
                "#",
                f"expected: {' '.join(map(lambda x: str(x), global_vars.expected))}",
            ),
        ]

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            # print(pass_ast.decls_defs_blocks_instrs[0])
            # print(type(pass_ast.decls_defs_blocks_instrs[0]))
            print(pass_ast.__repr__(incl_filenode=True)[1:])

        match pass_ast:
            case pn.File(pn.Name(val)):
                # insert at the beginning of the file
                with open(
                    val,
                    "w",
                    encoding="utf-8",
                ) as fout:
                    # metadata = f"# input: {' '.join(map(lambda x: str(x), global_vars.input))}\n# expected: {' '.join(map(lambda x: str(x), global_vars.expected))}\n"
                    fout.write(str(pass_ast)[1:])
            case _:
                throw_error(pass_ast)


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
        "--testmode",
        action="store_true",
        help="Read input and expected output from .input and .expected_output files",
    )
    parser.add_argument(
        "-T",
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
        help="Include metadata comments from first specified .picoc file into final .reti file",
    )
    # ------------------------------- Preprocessor ----------------------------
    parser.add_argument(
        "-I",
        "--include",
        dest="I",
        action="append",
        default=[],
        help="Add an include path (can be used multiple times)",
    )
    parser.add_argument(
        "-M",
        "--max-depth",
        type=int,
        default=200,
        help="Maximum include depth",
    )
    # ---------------------------------- Linker -------------------------------
    parser.add_argument(
        "-o",
        "--output_name",
        type=str,
        default="a.reti",
        help="Name of the output binary (default: a.reti)",
    )
    parser.add_argument(
        "-c",
        "--compile",
        action="store_true",
        help="Compile source files without linking (like gcc -c)",
    )

    global_vars.args = parser.parse_args()


def _set_terminal_size():
    size = shutil.get_terminal_size(fallback=(72, 24))
    if sys.stdin.isatty():
        global_vars.terminal_columns, global_vars.terminal_lines = (
            size.columns,
            size.lines,
        )


def _install_post_mortem_hook():
    if not global_vars.args.debug:
        return

    # Ensure unhandled exceptions drop into the debugger directly.
    sys.excepthook = db.debug_excepthook


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


def _get_test_metadata():
    if global_vars.args.metadata_comments:
        # the first specified .picoc file needs to inlcude the metadata comment
        with open(global_vars.args.infiles[0], encoding="utf-8") as fin:
            code = fin.read()

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
    elif global_vars.args.testmode:
        if os.path.isfile(global_vars.tstate.path_without_ext + ".input"):
            with open(
                global_vars.tstate.path_without_ext + ".input", "r", encoding="utf-8"
            ) as fin:
                global_vars.input = [
                    int(line)
                    for line in fin.readline().replace("\n", "").split(" ")
                    if line.lstrip("-").isdigit()
                ]
        if os.path.isfile(global_vars.tstate.path_without_ext + ".expected_output"):
            with open(
                global_vars.tstate.path_without_ext + ".expected_output", "r", encoding="utf-8"
            ) as fin:
                global_vars.expected = [
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
