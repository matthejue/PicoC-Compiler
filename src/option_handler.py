from src import global_vars
from src import symbol_table as st
from src import picoc_nodes as pn
from src import debug as db
import sys
import shutil
from src.ast_node import ASTNode
from src.ast_transformers import TransformerPicoC, TransformerRetiBlocks
from src.passes import Passes
from src.utils.util_funs_dependent import (
    remove_ext,
    throw_error,
    subheading,
    get_ext,
)
import subprocess, os, platform
import re
import argparse
import shlex
import json
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
        files = _expand_dependency_metadata(list(global_vars.args.infiles))
        global_vars.args.infiles = files
        build_targets = _normalize_input_units(files)

        if global_vars.args.generate_debuginfo and global_vars.args.compile:
            print("[ERROR] '-g/--generate_debuginfo' is not supported together with '--compile'")
            exit(1)
        if global_vars.args.generate_debuginfo and any(
            target["kind"] != "picoc" for target in build_targets
        ):
            print("[ERROR] '-g/--generate_debuginfo' only works when all inputs are '.picoc' files")
            exit(1)

        picoc_files = [f for f in files if get_ext(f) == "picoc"]
        if picoc_files:
            _syntax_check(picoc_files)
        if not files:
            return

        results = []

        if global_vars.args.intermediate_stages:
            for target in build_targets:
                try:
                    result = self.build_file(target)
                    results.append(result)  # store filename + return value
                except Exception as e:
                    if global_vars.args.debug:
                        raise  # let the post-mortem hook handle it
                    print(f"[ERROR] {target['path']}: {e}")
                    if global_vars.args.traceback:
                        traceback.print_exc()
                    exit(1)
        else:
            with ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="builder"
            ) as ex:
                fut_for = {
                    ex.submit(self.build_file, target): target
                    for target in build_targets
                }
                for fut in as_completed(fut_for):
                    target = fut_for[fut]
                    try:
                        result = fut.result()
                        results.append(result)
                    except Exception as e:
                        if global_vars.args.debug:
                            raise  # let the post-mortem hook handle it
                        print(f"[ERROR] {target['path']}: {e}")
                        if global_vars.args.traceback:
                            traceback.print_exc()
                        exit(1)

        asts, symbol_tables, all_file_blocks = (
            map(list, zip(*results)) if results else ([], [], [])
        )

        _get_test_metadata()

        if not global_vars.args.compile:
            self._insert_start_fun(asts, symbol_tables, all_file_blocks)
            self._link(asts, symbol_tables, all_file_blocks)

    def build_file(self, target):
        path = target["path"]
        global_vars.tstate.path_without_ext = remove_ext(path)
        global_vars.tstate.input_path = path

        target_kind = target["kind"]
        match target_kind:
            case "picoc":
                preprocessed_code = self._preprocess(path)
                return self._compl(preprocessed_code)
            case "reti_blocks":
                return self._load_external_reti_blocks(path, target["json_path"])
            case _:
                print(f"filename: {path}")
                print(f"File with extension '.{target_kind}' is not supported")
                exit(1)

    def _load_external_reti_blocks(self, path: str, json_path: str):
        with open(path, encoding="utf-8") as fin:
            code = fin.read()

        transformer = TransformerRetiBlocks()
        ts_tree = transformer.parse_tree(code)
        reti_blocks = transformer.build_ast(ts_tree, code)

        symbol_table = st.SymbolTable.load_json(json_path)
        all_blocks = {}
        for block in reti_blocks.decls_defs_blocks_instrs:
            match block:
                case pn.Block(name, _):
                    all_blocks[name] = block
                case _:
                    throw_error(block)

        if global_vars.args.intermediate_stages:
            print(subheading("RETI Blocks", "-"))
            print(reti_blocks.__repr__(incl_filenode=True)[1:])
            print(subheading("Symbol Table", "-"))
            print(symbol_table.to_json_str(pretty=True))

        return reti_blocks, symbol_table, all_blocks

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
        self._output_preprocess(code, "Preprocessed Code", ".pre")

        transformer = TransformerPicoC()
        ts_tree = transformer.parse_tree(code)

        # Always emit tokens/parse tree even if AST construction fails
        self._tokens_option(ts_tree, code, "Tokens")
        self._dt_pass(ts_tree, code, "Parse Tree")

        try:
            ast = transformer.build_ast(ts_tree, code)
        except Exception as exc:
            if global_vars.args.debug:
                raise
            print(f"[ERROR] AST transform failed: {exc}")
            if global_vars.args.traceback:
                traceback.print_exc()
            exit(1)

        self._output_pass(ast, "Abstract Syntax Tree")

        passes = Passes()
        picoc_shrink = passes.picoc_shrink(ast)
        self._output_pass(picoc_shrink, "PicoC Shrink")

        picoc_blocks = passes.picoc_blocks(picoc_shrink)
        self._output_pass(picoc_blocks, "PicoC Blocks")

        picoc_symbol = passes.picoc_symbol(picoc_blocks)
        self._output_pass(picoc_symbol, "PicoC Symbol")
        self._st_pass(
            passes.symbol_table,
            "Symbol Table",
            compl_opt_active=global_vars.args.compile,
        )

        picoc_typing = passes.picoc_typing(picoc_symbol)
        self._output_pass(picoc_typing, "PicoC Typing")

        picoc_anf = passes.picoc_anf(picoc_typing)
        self._output_pass(picoc_anf, "PicoC ANF")

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
        if global_vars.args.generate_debuginfo:
            self._write_debuginfo(reti)

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
                                sys.exit(1)

                case _:
                    print(
                        f"[error] Unexpected AST node (expected File), got: {type(file_ast).__name__}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

        main_func = None
        for symbol_table in symbol_tables:
            if symbol_table.contains("main", scope="global"):
                main_func = symbol_table._table["global"]["main"]
                break

        if main_func is None:
            print(
                "[error] No 'main' function found in any symbol table.", file=sys.stderr
            )
            sys.exit(1)

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

        def struct_completeness(symbol):
            datatype = symbol.get("datatype") if isinstance(symbol, dict) else None
            if isinstance(datatype, pn.StructDecl):
                return "complete"
            if isinstance(datatype, pn.StructSpec):
                return "incomplete"
            return None

        def is_struct_scope(scope):
            struct_symbol = merged_table.get("global", {}).get(scope)
            return struct_completeness(struct_symbol) == "complete"

        def merge_symbol(scope, name, incoming):
            existing = merged_table[scope].get(name)
            if existing is None:
                merged_table[scope][name] = dict(incoming)
                return

            existing_struct = struct_completeness(existing)
            incoming_struct = struct_completeness(incoming)
            existing_dt = existing.get("datatype")
            incoming_dt = incoming.get("datatype")

            if existing_struct and incoming_struct:
                # Structs are compile-time types, so repeated
                # header-provided definitions can share the existing entry.
                if existing_struct == "complete" and incoming_struct == "complete":
                    return
                # Struct forward declarations are incomplete symbols. A full
                # struct definition must always win over a forward declaration,
                # independent of file merge order.
                elif existing_struct == "incomplete" and incoming_struct == "complete":
                    merged_table[scope][name] = dict(incoming)
                elif existing_struct == "complete" and incoming_struct == "incomplete":
                    return
                elif existing_struct == "incomplete" and incoming_struct == "incomplete":
                    return
            elif is_struct_scope(scope):
                # Repeated headers duplicate struct attributes too; they are layout
                # metadata inside the type, not separate runtime symbols.
                return
            elif isinstance(existing_dt, pn.FunDecl) and isinstance(incoming_dt, pn.FunDecl):
                # Repeated declarations are fine; the syntax checker rejects
                # multiple definitions before symbol tables are merged.
                return
            else:
                throw_error(f"Duplicate symbol '{name}' in scope '{scope}'")

        # Merge all symbol tables
        for symbol_table in symbol_tables:
            for scope, symbols in symbol_table.items():
                if scope == "__parents__":
                    for k, v in symbols.items():
                        merged_parents[k] = v
                else:
                    merged_table.setdefault(scope, {})
                    for symbol_name, symbol in symbols.items():
                        merge_symbol(scope, symbol_name, symbol)

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

    def _tokens_option(self, ts_tree, code, heading):
        leaf_tokens = list(_iter_tokens(ts_tree, code))

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(leaf_tokens)

        if global_vars.args.write_files:
            with open(
                global_vars.tstate.path_without_ext + ".tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(leaf_tokens))

    def _dt_pass(self, ts_tree, code, heading):
        include_unnamed = bool(global_vars.args.double_verbose)
        formatted_tree = _format_tree(
            ts_tree.root_node, code, include_unnamed=include_unnamed
        )

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(formatted_tree)

        if global_vars.args.write_files:
            with open(
                global_vars.tstate.path_without_ext + ".dt",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(formatted_tree)

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

    def _output_preprocess(self, text: str, heading: str, suffix: str):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(text)

        if global_vars.args.write_files:
            with open(
                global_vars.tstate.path_without_ext + suffix,
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(text)

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

    def _write_debuginfo(self, pass_ast: pn.File):
        match pass_ast:
            case pn.File(pn.Name(val), instrs):
                files = []
                file_ids = {}
                ranges = []
                current_range = None
                # Instruction line numbers in debuginfo.json are 1-based,
                # matching source-code line numbers.
                line_no = 0

                for instr in instrs:
                    if isinstance(instr, pn.SingleLineComment):
                        continue
                    line_no += 1

                    source_file = getattr(instr, "source_file", None)
                    source_line = getattr(instr, "source_line", None)
                    if source_file is None or source_line is None:
                        current_range = None
                        continue

                    file_id = file_ids.get(source_file)
                    if file_id is None:
                        file_id = len(files)
                        file_ids[source_file] = file_id
                        files.append(source_file)

                    if (
                        current_range is not None
                        and current_range["file_id"] == file_id
                        and current_range["line"] == source_line
                        and current_range["end"] + 1 == line_no
                    ):
                        current_range["end"] = line_no
                    else:
                        current_range = {
                            "start": line_no,
                            "end": line_no,
                            "file_id": file_id,
                            "line": source_line,
                        }
                        ranges.append(current_range)

                debuginfo_path = Path(val).resolve().parent / "debuginfo.json"
                with open(debuginfo_path, "w", encoding="utf-8") as fout:
                    json.dump({"files": files, "ranges": ranges}, fout, indent=2)
                    fout.write("\n")
            case _:
                throw_error(pass_ast)


def _iter_tokens(tree, code):
    def dfs(node):
        if not node.children:
            # Only emit token type and value to keep debug output concise
            yield (node.type, code[node.start_byte : node.end_byte])
        else:
            for child in node.children:
                yield from dfs(child)

    yield from dfs(tree.root_node)


def _format_tree(node, code, depth: int = 0, *, include_unnamed: bool = False):
    lines = []
    code_bytes = code if isinstance(code, (bytes, bytearray)) else code.encode("utf-8")

    def walk(n, d):
        snippet = code_bytes[n.start_byte : n.end_byte].decode("utf-8").replace(
            "\n", "\\n"
        )
        lines.append(f"{'  '*d}{n.type}: {snippet}")
        for child in n.children:
            if include_unnamed or child.is_named:
                walk(child, d + 1)

    walk(node, depth)
    return "\n".join(lines)


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
    parser.add_argument(
        "-g",
        "--generate_debuginfo",
        action="store_true",
        help="Write debuginfo.json for linked '.picoc' inputs",
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


def _expand_dependency_metadata(files: List[str]) -> List[str]:
    if not files or get_ext(files[0]) != "picoc":
        return files

    dependencies = _read_dependency_metadata(files[0])
    if not dependencies:
        return files

    seen = set()
    expanded = []
    for path in files + dependencies:
        key = os.path.abspath(path)
        if key in seen:
            continue
        seen.add(key)
        expanded.append(path)
    return expanded

def _normalize_input_units(files: List[str]) -> List[Dict[str, str]]:
    json_by_base: Dict[str, str] = {}
    reti_block_bases_with_matching_json = set()

    for path in files:
        if get_ext(path) != "json":
            continue
        # Canonicalize relative spellings like "x/y.json" vs "./x/y.json".
        base_path = os.path.abspath(remove_ext(path))
        if base_path in json_by_base:
            print(
                f"[ERROR] Multiple .json files were provided for '{base_path}.reti_blocks'"
            )
            sys.exit(1)
        json_by_base[base_path] = path

    build_targets: List[Dict[str, str]] = []
    for path in files:
        extension = get_ext(path)
        match extension:
            case "picoc":
                build_targets.append({"kind": "picoc", "path": path})
            case "reti_blocks":
                # Use the same canonicalized base-path key as above.
                base_path = os.path.abspath(remove_ext(path))
                explicit_json_path = json_by_base.get(base_path)
                if explicit_json_path is None:
                    auto_json_path = remove_ext(path) + ".json"
                    if os.path.isfile(auto_json_path):
                        json_path = auto_json_path
                    else:
                        print(
                            f"[ERROR] Missing companion .json symbol table for '{path}'. "
                            "Pass the matching .json file as input or place it next to the "
                            ".reti_blocks file."
                        )
                        sys.exit(1)
                else:
                    json_path = explicit_json_path
                    # Reached when a matching `.json` path was provided explicitly
                    # in the input list, but that path does not currently exist.
                    if not os.path.isfile(json_path):
                        print(
                            f"[ERROR] Companion .json symbol table '{json_path}' was not found"
                        )
                        sys.exit(1)
                reti_block_bases_with_matching_json.add(base_path)
                build_targets.append(
                    {
                        "kind": "reti_blocks",
                        "path": path,
                        "json_path": json_path,
                    }
                )
            case "json":
                continue
            case _:
                print(f"[ERROR] File '{path}' has unsupported extension '.{extension}'")
                sys.exit(1)

    for base_path, json_path in json_by_base.items():
        if base_path not in reti_block_bases_with_matching_json:
            print(
                f"[ERROR] Standalone .json input '{json_path}' has no matching "
                ".reti_blocks input"
            )
            sys.exit(1)

    return build_targets


def _read_dependency_metadata(source_path: str) -> List[str]:
    source_dir = os.path.dirname(source_path) or "."
    dependencies: List[str] = []
    in_block_comment = False

    try:
        with open(source_path, encoding="utf-8") as fin:
            lines = fin.readlines()
    except OSError as exc:
        print(f"[ERROR] Could not read dependency metadata from '{source_path}': {exc}")
        sys.exit(1)

    for line in lines:
        stripped = line.strip()

        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue
        if not stripped:
            continue
        if stripped.startswith("/*"):
            in_block_comment = "*/" not in stripped
            continue

        match = re.match(r"^\s*//\s*dependencies\s*:\s*(.*?)\s*$", line)
        if match:
            try:
                dependency_specs = shlex.split(match.group(1))
            except ValueError as exc:
                print(f"[ERROR] Invalid dependencies metadata in '{source_path}': {exc}")
                sys.exit(1)
            dependencies.extend(
                _resolve_dependency_path(source_dir, dependency)
                for dependency in dependency_specs
            )
            continue

        if stripped.startswith("//"):
            continue
        break

    return dependencies


def _resolve_dependency_path(source_dir: str, dependency: str) -> str:
    if os.path.isabs(dependency):
        candidates = [dependency]
    else:
        candidates = [dependency, os.path.join(source_dir, dependency)]

    for candidate in candidates:
        if os.path.isfile(candidate):
            resolved = os.path.normpath(candidate)
            if get_ext(resolved) not in {"picoc", "reti_blocks", "json"}:
                print(
                    f"[ERROR] Dependency '{dependency}' has unsupported extension. "
                    "Only .picoc, .reti_blocks, and .json dependencies are supported."
                )
                sys.exit(1)
            return resolved

    print(f"[ERROR] Dependency '{dependency}' was not found")
    sys.exit(1)


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
        "-std=gnu11",
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
