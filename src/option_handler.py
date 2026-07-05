from src import global_vars
from src import symbol_table as st
from src import picoc_nodes as pn
from src import debug as db
import sys
import shutil
from src.ast_node import ASTNode
from src.ast_transformers import TransformerPicoC, TransformerRetiBlocks
from src.passes import Passes
from src.passes.compilation import opt_level_1
from src.utils.util_funs_dependent import (
    remove_ext,
    throw_error,
    subheading,
    get_ext,
)
from src.utils.util_funs_independent import convert_to_single_line
import subprocess, os, platform
import re
import shlex
import json
from src.preprocessor import Preprocessor
from typing import Iterable, List, Optional, Dict, Any, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import traceback
from typing import cast
from src.cli_args import build_parser


SECTION_ORDER = ["ivt", "text", "data"]
TEXT_SECTION = "text"
DATA_SECTION = "data"
MEMORY_CONSTANTS_HEADER_NAME = "memory_constants.header"
SRAM_BASE_ADDRESS = -(2**31)
SRAM_SIZE = 2**18
SRAM_MAX_ADDRESS = SRAM_SIZE - 1
DEFAULT_KERNEL_STACK_START = 15000


def _flatten_reti_entries(entries):
    flat_entries = []
    for entry in entries:
        match entry:
            case pn.Section(_, section_entries):
                flat_entries.extend(_flatten_reti_entries(section_entries))
            case pn.Block(_, block_entries):
                flat_entries.extend(_flatten_reti_entries(block_entries))
            case _:
                flat_entries.append(entry)
    return flat_entries


def _pass_output_text(pass_ast: pn.File):
    return str(pass_ast)[1:]


def _walk_blocks(items):
    for item in items:
        match item:
            case pn.Section(_, entries):
                yield from _walk_blocks(entries)
            case pn.Block():
                yield item


def _remove_blocks_named(items, block_name: str):
    removed = []
    kept = []
    for item in items:
        match item:
            case pn.Section(name, entries):
                section_removed, section_kept = _remove_blocks_named(entries, block_name)
                removed.extend(section_removed)
                kept.append(pn.Section(name, section_kept))
            case pn.Block(name, stmts) if name == block_name:
                removed.extend(stmts)
            case _:
                kept.append(item)
    return removed, kept


def _merge_sectioned_items(asts):
    sections = {name: [] for name in SECTION_ORDER}
    loose_text_entries = []

    for ast in asts:
        for item in ast.decls_defs_blocks_instrs:
            match item:
                case pn.Section(name, entries) if name in sections:
                    sections[name].extend(entries)
                case pn.Block():
                    loose_text_entries.append(item)
                case _:
                    loose_text_entries.append(item)

    sections[TEXT_SECTION][:0] = loose_text_entries
    return [pn.Section(name, sections[name]) for name in SECTION_ORDER]


def _function_block_owner(block_name: str, function_names):
    matches = [
        fun_name
        for fun_name in function_names
        if (
            block_name == fun_name
            or block_name.startswith(f"{fun_name}_")
            or block_name.startswith(f"{fun_name}.")
        )
    ]
    if not matches:
        return None
    return max(matches, key=len)


def _apply_function_sections(items, symbol_table):
    function_names = set()
    sectioned_functions = set()
    for fun_name, sym in symbol_table._table.get("global", {}).items():
        datatype = sym.get("datatype") if isinstance(sym, dict) else None
        if isinstance(datatype, pn.FunDecl):
            function_names.add(fun_name)
            if sym.get("section") == "ivt":
                sectioned_functions.add(fun_name)

    if not sectioned_functions:
        return

    sections = {
        item.name: item.entries
        for item in items
        if isinstance(item, pn.Section)
    }
    ivt_entries = sections.get("ivt", [])
    text_entries = sections.get("text", [])
    text_kept = []

    for entry in text_entries:
        owner = (
            _function_block_owner(entry.name, function_names)
            if isinstance(entry, pn.Block)
            else None
        )
        if owner in sectioned_functions:
            entry.section = "ivt"
            ivt_entries.append(entry)
        else:
            text_kept.append(entry)

    text_entries[:] = text_kept


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
        if global_vars.args.kernelheader and global_vars.args.compile:
            print("[ERROR] '-k/--kernelheader' requires linking and is not supported together with '--compile'")
            exit(1)
        if global_vars.args.generate_debuginfo and not global_vars.args.kernelheader and any(
            target["kind"] != "picoc" for target in build_targets
        ):
            print("[ERROR] '-g/--generate_debuginfo' only works when all inputs are '.picoc' files")
            exit(1)
        if global_vars.args.generate_debuginfo and not (
            global_vars.args.intermediate_stages and global_vars.args.write_files
        ):
            print(
                "[warning] '-g/--generate_debuginfo' needs '-i/--intermediate_stages' "
                "and '-w/--write_files' to create the .pre file needed for debugging."
            )

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
                return self._load_external_reti_blocks(path, target["st_path"])
            case _:
                print(f"filename: {path}")
                print(f"File with extension '.{target_kind}' is not supported")
                exit(1)

    def _load_external_reti_blocks(self, path: str, st_path: str):
        with open(path, encoding="utf-8") as fin:
            code = fin.read()

        transformer = TransformerRetiBlocks()
        ts_tree = transformer.parse_tree(code)
        reti_blocks = transformer.build_ast(ts_tree, code)

        symbol_table = st.SymbolTable.load_json(st_path)
        all_blocks = {}
        for block in _walk_blocks(reti_blocks.decls_defs_blocks_instrs):
            match block:
                case pn.Block(name, _):
                    all_blocks[name] = block
                case _:
                    throw_error(block)

        if global_vars.args.intermediate_stages:
            print(subheading("RETI Blocks", "-"))
            print(_pass_output_text(reti_blocks))
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
        self._parse_tree_pass(ts_tree, code, "Parse Tree")

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
        passes = Passes()
        passes.all_blocks = {k: v for d in all_file_blocks for k, v in d.items()}
        passes.symbol_table = self._merge_symbol_tables(symbol_tables)
        merged_ast = self._merge_asts(asts, passes.symbol_table)
        self._combined_reti_blocks_pass(merged_ast)

        self._st_pass(passes.symbol_table, "Combined Symbol Table", is_global_st=True)

        reti_patch = passes.reti_patch(merged_ast)
        self._output_pass(
            reti_patch,
            "RETI Patch",
        )
        reti = passes.reti(reti_patch)
        self._reti_with_metadata(reti, "RETI", passes.reti_sections)
        if global_vars.args.generate_debuginfo and not global_vars.args.kernelheader:
            self._write_debuginfo(reti, passes.symbol_table, passes.reti_sections)

    def _insert_start_fun(self, asts, symbol_tables, all_file_blocks):
        passes = Passes()

        main_func = None
        for symbol_table in symbol_tables:
            if symbol_table.contains("main", scope="global"):
                main_func = symbol_table._table["global"]["main"]
                break

        if main_func is None:
            print(
                "[warning] No main function found; no _start block will be generated, so the output may not be directly executable.",
                file=sys.stderr,
            )
            return

        global_inits = []
        for file_ast in asts:
            match file_ast:
                case pn.File(_, items):
                    removed, kept = _remove_blocks_named(items, "_global_inits")
                    global_inits.extend(removed)
                    file_ast.decls_defs_blocks_instrs[:] = kept

                case _:
                    print(
                        f"[error] Unexpected AST node (expected File), got: {type(file_ast).__name__}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

        passes.symbol_table.declare("main", main_func, scope="global")

        start_block = pn.Block(
            "_start",
            passes._picoc_anf_stmt(pn.Exp(pn.Call(pn.Name("main"), [])))
            + [pn.Exit(pn.Num("0"))],
        )
        start_block.show_id_comment = True
        passes._register_block(start_block, "global")
        start_blocks = []
        passes._split_call_continuations(start_block, start_blocks)

        start_ast = pn.File(pn.Name("start"), start_blocks)

        reti_blocks: pn.File = passes.reti_blocks(start_ast)
        start_reti_blocks_path = (
            remove_ext(global_vars.args.output_name) + "_startprogram.reti_blocks"
        )
        reti_blocks.name = pn.Name(start_reti_blocks_path)
        self._output_pass(reti_blocks, "RETI Blocks")

        start_blocks = list(_walk_blocks(reti_blocks.decls_defs_blocks_instrs))
        if not start_blocks:
            print("[error] Internal error: generated _start has no RETI block.", file=sys.stderr)
            sys.exit(1)
        start_blocks[0].stmts_instrs[:0] = global_inits

        # Insert at the beginning so _start comes first
        asts.insert(0, reti_blocks)
        symbol_tables.insert(0, passes.symbol_table)
        all_file_blocks.insert(0, passes.all_blocks)

    def _merge_asts(self, asts, symbol_table=None):
        global_vars.tstate.path_without_ext = remove_ext(global_vars.args.output_name)

        if not asts:
            return pn.File(pn.Name(global_vars.args.output_name), _merge_sectioned_items([]))

        merged_decls_defs_blocks_instrs = _merge_sectioned_items(asts)
        if symbol_table is not None:
            _apply_function_sections(merged_decls_defs_blocks_instrs, symbol_table)
        if opt_level_1.enabled(global_vars.args) and symbol_table is not None:
            for item in merged_decls_defs_blocks_instrs:
                match item:
                    case pn.Section("data", entries):
                        item.entries = opt_level_1.ordered_data_entries(
                            entries, symbol_table
                        )

        # return a new merged File node
        return pn.File(pn.Name(global_vars.args.output_name), merged_decls_defs_blocks_instrs)

    def _merge_symbol_tables(self, symbol_tables):
        if not symbol_tables:
            symbol_table = st.SymbolTable()
            return symbol_table

        merged_table = {}
        merged_parents = {}

        def symbol_signature(value):
            match value:
                case pn.ASTNode():
                    return (
                        value.__class__.__name__,
                        tuple(
                            sorted(
                                (attr_name, symbol_signature(attr_value))
                                for attr_name, attr_value in vars(value).items()
                                if attr_name not in {
                                    "source_file",
                                    "source_line",
                                    "suppress_source_origin",
                                }
                            )
                        ),
                    )
                case dict():
                    return tuple(
                        sorted(
                            (key, symbol_signature(item))
                            for key, item in value.items()
                        )
                    )
                case list():
                    return tuple(symbol_signature(item) for item in value)
                case _:
                    return value

        def symbols_equivalent(existing, incoming):
            return symbol_signature(existing) == symbol_signature(incoming)

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
                # Repeated function declarations are fine. Definitions are stored
                # as FunDecl too; normally they should overwrite declarations,
                # because declarations may omit parameter names. In PicoC,
                # however, function declarations require named parameters.
                # Syntax checking rejects duplicate definitions before merging.
                if existing.get("section") is None and incoming.get("section") is not None:
                    existing["section"] = incoming["section"]
                    existing_dt.section = incoming["section"]
                return
            elif scope != "global" and symbols_equivalent(existing, incoming):
                # Re-including the same source file can replay the same function
                # scope symbols. If the merged payload is identical, keep the
                # existing entry instead of treating it as a conflict.
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

        data_addr = 0
        ivt_addr = 0
        for sym_name, sym in merged_table["global"].items():
            if "addr" in sym and "size" in sym:
                if sym.get("section") == "ivt":
                    sym["addr"] = ivt_addr
                    ivt_addr += sym["size"]
                else:
                    sym["addr"] = data_addr
                    data_addr += sym["size"]

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

        if global_vars.args.write_files and not global_vars.args.kernelheader:
            with open(
                global_vars.tstate.path_without_ext + ".tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(leaf_tokens))

    def _parse_tree_pass(self, ts_tree, code, heading):
        include_unnamed = bool(global_vars.args.double_verbose)
        formatted_tree = _format_tree(
            ts_tree.root_node, code, include_unnamed=include_unnamed
        )

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(formatted_tree)

        if global_vars.args.write_files and not global_vars.args.kernelheader:
            with open(
                global_vars.tstate.path_without_ext + ".ps",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(formatted_tree)

    def _output_pass(self, pass_ast: pn.File, heading, *, compl_opt_active=False):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(_pass_output_text(pass_ast))

        if (global_vars.args.write_files or compl_opt_active) and not global_vars.args.kernelheader:
            match pass_ast:
                case pn.File(pn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(_pass_output_text(pass_ast))
                case _:
                    throw_error(pass_ast)

    def _combined_reti_blocks_pass(self, pass_ast: pn.File):
        if not global_vars.args.intermediate_stages:
            return

        print(subheading("Combined RETI Blocks", "-"))
        print(_pass_output_text(pass_ast))

        if global_vars.args.write_files and not global_vars.args.kernelheader:
            output_path = remove_ext(global_vars.args.output_name) + "_combined.reti_blocks"
            with open(output_path, "w", encoding="utf-8") as fout:
                fout.write(_pass_output_text(pass_ast))

    def _output_preprocess(self, text: str, heading: str, suffix: str):
        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(text)

        if global_vars.args.write_files and not global_vars.args.kernelheader:
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

        if (global_vars.args.write_files or compl_opt_active) and not global_vars.args.kernelheader:
            with open(
                global_vars.tstate.path_without_ext + ".st",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(json_symbol_table))

    def _reti_with_metadata(self, pass_ast: pn.File, heading, sections):
        metadata_entries = []
        # Prefer raw metadata_comments strings (from // in: and // expected: comments)
        for key in ("input", "expected", "datasegment"):
            value = global_vars.metadata_comments.get(key) if global_vars.metadata_comments else None
            if value is not None:
                metadata_entries.append(pn.SingleLineComment("#", f"{key}:{value}"))
        
        # Fallback: reconstruct from parsed input/expected if not in metadata_comments
        if "input" not in (global_vars.metadata_comments or {}):
            if global_vars.input:
                metadata_entries.append(pn.SingleLineComment(
                    "#", f"input: {' '.join(map(lambda x: str(x), global_vars.input))}"
                ))
        if "expected" not in (global_vars.metadata_comments or {}):
            if global_vars.expected:
                metadata_entries.append(pn.SingleLineComment(
                    "#", f"expected: {' '.join(map(lambda x: str(x), global_vars.expected))}"
                ))

        pass_ast.decls_defs_blocks_instrs[:0] = metadata_entries

        if global_vars.args.intermediate_stages:
            print(subheading(heading, "-"))
            print(_pass_output_text(pass_ast))

        if global_vars.args.kernelheader:
            self._write_memory_constants_header(sections)
            return

        match pass_ast:
            case pn.File(pn.Name(val)):
                # insert at the beginning of the file
                with open(
                    val,
                    "w",
                    encoding="utf-8",
                ) as fout:
                    # metadata = f"# input: {' '.join(map(lambda x: str(x), global_vars.input))}\n# expected: {' '.join(map(lambda x: str(x), global_vars.expected))}\n"
                    fout.write(_pass_output_text(pass_ast))
                self._write_reti_sections(sections, val)
            case _:
                throw_error(pass_ast)

    def _write_reti_sections(self, sections, reti_path: str):
        sections_text = json.dumps(sections, indent=2)
        if global_vars.args.intermediate_stages:
            print(subheading("RETI Sections", "-"))
            print(sections_text)

        sections_path = Path(reti_path).with_suffix(".sections")
        with open(sections_path, "w", encoding="utf-8") as fout:
            fout.write(sections_text + "\n")

    def _memory_constants_header_path(self) -> Path:
        output_path = Path(global_vars.args.output_name)
        return output_path.parent / MEMORY_CONSTANTS_HEADER_NAME

    def _sram_address(self, offset: int) -> int:
        return SRAM_BASE_ADDRESS + offset

    def _kernel_stack_start(self, sections) -> int:
        stack_start = int(sections["stack_start"])
        if stack_start == -1:
            return DEFAULT_KERNEL_STACK_START
        return stack_start

    def _sram_memory_constants_lines(self, sections) -> List[str]:
        codesegment_start = int(sections["codesegment_start"])
        datasegment_start = int(sections["datasegment_start"])
        heap_start = int(sections["heap_start"])
        stack_start = self._kernel_stack_start(sections)
        cs_start_address = self._sram_address(codesegment_start)
        ds_start_address = self._sram_address(datasegment_start)
        sp_start_address = self._sram_address(stack_start)
        return [
            "#define SRAM_BASE (-2147483647 - 1) // -2^31",
            f"#define SRAM_MAX_ADDRESS {SRAM_MAX_ADDRESS} // 2^18 - 1",
            f"#define KERNEL_HEAP_START {heap_start} // heap_start",
            f"#define PROCESS_MEMORY_START {sp_start_address + 1} // -2^31 + stack_start + 1",
            f'#define KERNEL_CS_START_ASM "LOADI32 CS {cs_start_address}" // -2^31 + codesegment_start',
            f'#define KERNEL_DS_START_ASM "LOADI32 DS {ds_start_address}" // -2^31 + datasegment_start',
            f'#define KERNEL_SP_START_ASM "LOADI32 SP {sp_start_address}" // -2^31 + stack_start',
            f'#define KERNEL_CS_ACC_ASM "LOADI32 ACC {cs_start_address}" // -2^31 + codesegment_start',
        ]

    def _eprom_memory_constants_lines(self, sections) -> List[str]:
        datasegment_start = int(sections["datasegment_start"])
        eprom_stack_address = self._sram_address(SRAM_MAX_ADDRESS)
        return [
            f"#define SRAM_MAX_ADDRESS {SRAM_MAX_ADDRESS} // 2^18 - 1",
            f'#define EPROM_DS_START_ASM "LOADI32 DS {datasegment_start}" // datasegment_start',
            f'#define EPROM_STACK_START_ASM "LOADI32 SP {eprom_stack_address}" // -2^31 + 2^18 - 1',
        ]

    def _memory_constants_lines(self, sections) -> List[str]:
        match global_vars.args.kernelheader:
            case "sram":
                return self._sram_memory_constants_lines(sections)
            case "eprom":
                return self._eprom_memory_constants_lines(sections)
            case _:
                throw_error(f"Unknown kernel header mode: {global_vars.args.kernelheader}")

    def _write_memory_constants_header(self, sections):
        header_path = self._memory_constants_header_path()
        updated_lines = self._memory_constants_lines(sections)
        header_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    def _debug_json_value(self, value):
        if isinstance(value, pn.Empty):
            return None
        if isinstance(value, pn.Num):
            return int(value.val)
        if isinstance(value, (int, float, str, bool)) or value is None:
            return value
        return convert_to_single_line(value)

    def _debug_runtime_symbols(self, symbol_table: st.SymbolTable):
        variables = []
        arguments = []
        for scope, symbols in symbol_table.items():
            if scope == "__parents__":
                continue
            for symbol_name, symbol in symbols.items():
                if not isinstance(symbol, dict) or "frame_kind" not in symbol:
                    continue

                entry = {
                    "name": symbol.get("name", symbol_name),
                    "scope": scope,
                    "address": self._debug_json_value(symbol.get("addr")),
                    "size": self._debug_json_value(symbol.get("size")),
                }

                if symbol.get("frame_kind") == "param":
                    arguments.append(entry)
                else:
                    variables.append(entry)

        return variables, arguments

    def _debug_target_in_text_section(
        self,
        symbol_table: st.SymbolTable,
        target_function,
    ):
        if target_function is None:
            return False
        symbol, _ = symbol_table.resolve(target_function, scope="global")
        return not isinstance(symbol, dict) or symbol.get("section") != "ivt"

    def _debug_source_file(self, source_file):
        source_path = Path(source_file)
        if source_path.suffix == ".picoc":
            return str(source_path.with_suffix(".pre"))
        return source_file

    def _write_debuginfo(
        self,
        pass_ast: pn.File,
        symbol_table: st.SymbolTable,
        sections,
    ):
        match pass_ast:
            case pn.File(pn.Name(val), instrs):
                variables, arguments = self._debug_runtime_symbols(symbol_table)
                codesegment_start = sections.get("codesegment_start", 0)
                datasegment_start = sections.get("datasegment_start")
                instrs = _flatten_reti_entries(instrs)
                files = []
                file_ids = {}
                ranges = []
                call_jumps = []
                return_addresses = []
                current_range = None
                # Instruction line numbers in the .debuginfo file are 1-based,
                # matching source-code line numbers.
                instr_idx = 0

                for instr in instrs:
                    if isinstance(instr, pn.SingleLineComment):
                        continue
                    absolute_addr = instr_idx
                    instr_idx += 1
                    if absolute_addr < codesegment_start:
                        continue
                    if (
                        datasegment_start is not None
                        and absolute_addr >= datasegment_start
                    ):
                        break
                    text_addr = absolute_addr - codesegment_start
                    line_no = text_addr + 1

                    call_target_function = getattr(instr, "call_target_function", None)
                    indirect_call = getattr(instr, "indirect_call", False)
                    if indirect_call or self._debug_target_in_text_section(
                        symbol_table,
                        call_target_function,
                    ):
                        call_jumps.append(
                            {
                                "address": text_addr,
                                "target_function": call_target_function,
                                "indirect": indirect_call,
                            }
                        )
                    if getattr(instr, "return_statement", False):
                        return_addresses.append(text_addr)

                    source_file = getattr(instr, "source_file", None)
                    source_line = getattr(instr, "source_line", None)
                    if (source_file is None) != (source_line is None):
                        throw_error(instr)
                    # The fields are either both set or both unset, so checking
                    # one field is sufficient here.
                    if source_file is None:
                        current_range = None
                        continue
                    source_file = self._debug_source_file(source_file)

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

                debuginfo_path = Path(val).with_suffix(".debuginfo")
                with open(debuginfo_path, "w", encoding="utf-8") as fout:
                    json.dump(
                        {
                            "files": files,
                            "ranges": ranges,
                            "variables": variables,
                            "arguments": arguments,
                            "call_jumps": call_jumps,
                            "return_addresses": return_addresses,
                        },
                        fout,
                        indent=2,
                    )
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
    global_vars.args = build_parser().parse_args()


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
        "verbose",
        "double_verbose",
        "traceback",
        "debug",
        "supress_errors",
        "binary",
        "metadata_comments",
        "kernelheader",
        "optimization_level",
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
    st_by_base: Dict[str, str] = {}
    reti_block_bases_with_matching_st = set()

    for path in files:
        if get_ext(path) != "st":
            continue
        # Canonicalize relative spellings like "x/y.st" vs "./x/y.st".
        base_path = os.path.abspath(remove_ext(path))
        if base_path in st_by_base:
            print(
                f"[ERROR] Multiple .st files were provided for '{base_path}.reti_blocks'"
            )
            sys.exit(1)
        st_by_base[base_path] = path

    build_targets: List[Dict[str, str]] = []
    for path in files:
        extension = get_ext(path)
        match extension:
            case "picoc":
                build_targets.append({"kind": "picoc", "path": path})
            case "reti_blocks":
                # Use the same canonicalized base-path key as above.
                base_path = os.path.abspath(remove_ext(path))
                explicit_st_path = st_by_base.get(base_path)
                if explicit_st_path is None:
                    auto_st_path = remove_ext(path) + ".st"
                    if os.path.isfile(auto_st_path):
                        st_path = auto_st_path
                    else:
                        print(
                            f"[ERROR] Missing companion .st symbol table for '{path}'. "
                            "Pass the matching .st file as input or place it next to the "
                            ".reti_blocks file."
                        )
                        sys.exit(1)
                else:
                    st_path = explicit_st_path
                    # Reached when a matching `.st` path was provided explicitly
                    # in the input list, but that path does not currently exist.
                    if not os.path.isfile(st_path):
                        print(
                            f"[ERROR] Companion .st symbol table '{st_path}' was not found"
                        )
                        sys.exit(1)
                reti_block_bases_with_matching_st.add(base_path)
                build_targets.append(
                    {
                        "kind": "reti_blocks",
                        "path": path,
                        "st_path": st_path,
                    }
                )
            case "st":
                continue
            case _:
                print(f"[ERROR] File '{path}' has unsupported extension '.{extension}'")
                sys.exit(1)

    for base_path, st_path in st_by_base.items():
        if base_path not in reti_block_bases_with_matching_st:
            print(
                f"[ERROR] Standalone .st input '{st_path}' has no matching "
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
            if get_ext(resolved) not in {"picoc", "reti_blocks", "st"}:
                print(
                    f"[ERROR] Dependency '{dependency}' has unsupported extension. "
                    "Only .picoc, .reti_blocks, and .st dependencies are supported."
                )
                sys.exit(1)
            return resolved

    print(f"[ERROR] Dependency '{dependency}' was not found")
    sys.exit(1)


def _get_test_metadata():
    global_vars.metadata_comments = {}
    if global_vars.args.metadata_comments:
        # the first specified .picoc file needs to inlcude the metadata comment
        with open(global_vars.args.infiles[0], encoding="utf-8") as fin:
            code = fin.read()

        for line in code.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(
                r"^(//|#)\s*(input|in|expected|exp|datasegment|data)\s*:\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if match:
                raw_key = match.group(2).lower()
                value = match.group(3).strip()
                key = {
                    "in": "input",
                    "input": "input",
                    "exp": "expected",
                    "expected": "expected",
                    "data": "datasegment",
                    "datasegment": "datasegment",
                }[raw_key]
                global_vars.metadata_comments[key] = value
                continue
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*"):
                continue
            break

        input_comment = global_vars.metadata_comments.get("input")
        expected_comment = global_vars.metadata_comments.get("expected")
        global_vars.input = (
            [int(token) for token in input_comment.split() if token.lstrip("-").isdigit()]
            if input_comment
            else []
        )
        global_vars.expected = (
            [int(token) for token in expected_comment.split() if token.lstrip("-").isdigit()]
            if expected_comment
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
