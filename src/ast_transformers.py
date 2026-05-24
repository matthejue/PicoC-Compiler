import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from tree_sitter import Language, Parser

from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.ast_node import set_source_origin
from src.utils.util_funs_dependent import throw_error


def _load_ts_language(grammar_dir: str, library_name: str, symbol_name: str) -> Language:
    """
    Load a vendored Tree-sitter grammar so local grammar changes are used
    instead of the PyPI wheel.
    """
    grammar_lib = (
        Path(__file__).resolve().parent.parent
        / "vendor"
        / grammar_dir
        / library_name
    )
    if not grammar_lib.exists():
        raise FileNotFoundError(
            f"Tree-sitter grammar not found at {grammar_lib}. "
            f"Build the grammar in vendor/{grammar_dir}."
        )
    lib = ctypes.CDLL(str(grammar_lib))
    if not hasattr(lib, symbol_name):
        raise AttributeError(f"'{symbol_name}' symbol missing in {grammar_lib}")
    symbol = getattr(lib, symbol_name)
    symbol.restype = ctypes.c_void_p
    return Language(symbol())


_TS_PICOC_LANGUAGE: Language | None = None
_TS_RETI_LANGUAGE: Language | None = None


def _load_picoc_ts_language() -> Language:
    global _TS_PICOC_LANGUAGE
    if _TS_PICOC_LANGUAGE is None:
        _TS_PICOC_LANGUAGE = _load_ts_language(
            "tree-sitter-picoc",
            "picoc.so",
            "tree_sitter_picoc",
        )
    return _TS_PICOC_LANGUAGE


def _load_reti_ts_language() -> Language:
    global _TS_RETI_LANGUAGE
    if _TS_RETI_LANGUAGE is None:
        _TS_RETI_LANGUAGE = _load_ts_language(
            "tree-sitter-reti",
            "reti.so",
            "tree_sitter_reti",
        )
    return _TS_RETI_LANGUAGE


def _storage_class_specifiers(children):
    return [child for child in children if isinstance(child, (pn.Inline, pn.Static))]


def _without_storage_class_specifiers(children):
    return [child for child in children if not isinstance(child, (pn.Inline, pn.Static))]


class _TreeSitterTransformer:
    def __init__(self, language: Language):
        self.parser = Parser()
        self.parser.language = language
        self._code: str | None = None
        self._cache: dict[int, object] = {}

    def parse_tree(self, code: str):
        return self.parser.parse(code.encode("utf-8"))

    def build_ast(self, tree, code: str):
        self._code = code
        return self.walk(tree.root_node)

    def value(self, node) -> str:
        return self._code[node.start_byte : node.end_byte]

    def _named_children(self, node):
        return [c for c in node.children if c.is_named]

    def _unnamed_children(self, node):
        return [c for c in node.children if not c.is_named]

    def operator(self, node):
        unnamed = self._unnamed_children(node)
        if not unnamed:
            throw_error(f"No unnamed children found in node '{node.type}'")
        return self.value(unnamed[0])

    def walk(self, root):
        self._cache = {}
        stack = [(root, False)]
        while stack:
            node, done = stack.pop()
            if done:
                child_nodes = self._named_children(node)
                # Use id(node) as the cache key to ensure uniqueness and avoid issues if
                # parse tree node objects are not hashable or override __eq__/__hash__.
                child_vals = [self._cache[id(c)] for c in child_nodes]
                handler = getattr(self, node.type, self.generic)
                result = handler(node, child_vals)
                self._cache[id(node)] = self._attach_origin(result, node)
            else:
                stack.append((node, True))
                for child in reversed(self._named_children(node)):
                    stack.append((child, False))
        return self._cache[id(root)]

    def generic(self, _node, children):
        if len(children) == 1:
            return children[0]
        return children

    def _attach_origin(self, result, node):
        source_path = getattr(global_vars.tstate, "input_path", "")
        if source_path and (
            isinstance(result, pn.ASTNode) or isinstance(result, rn.ASTNode)
        ):
            # Tree-sitter rows are 0-based; store 1-based lines for debuginfo.
            set_source_origin(result, Path(source_path).name, node.start_point[0] + 1)
        return result


class TransformerPicoC(_TreeSitterTransformer):
    """
    Tree-sitter backed transformer that builds the PicoC AST using the
    vendored PicoC grammar from ../vendor/tree-sitter-picoc.
    """

    def __init__(self):
        super().__init__(_load_picoc_ts_language())

    def _bin_op(self, op: str):
        match op:
            case "+":
                return pn.Add()
            case "-":
                return pn.Sub()
            case "*":
                return pn.Mul()
            case "/":
                return pn.Div()
            case "%":
                return pn.Mod()
            case "^":
                return pn.Oplus()
            case "&":
                return pn.And()
            case "|":
                return pn.Or()
            case "&&":
                return pn.LogicAnd()
            case "||":
                return pn.LogicOr()
            case "==":
                return pn.Eq()
            case "!=":
                return pn.NEq()
            case "<":
                return pn.Lt()
            case "<=":
                return pn.LtE()
            case ">":
                return pn.Gt()
            case ">=":
                return pn.GtE()
        throw_error(f"Unsupported binary operator '{op}'")

    def _to_bool(self, node):
        match node:
            case pn.BinOp(_, pn.LogicAnd(), _) | pn.BinOp(_, pn.LogicOr(), _) | pn.Atom():
                return node
            case pn.UnOp(pn.LogicNot(), _):
                return node
            case (
                pn.Attr()
                | pn.Deref()
                | pn.Subscr()
                | pn.BinOp()
                | pn.UnOp()
                | pn.Num()
                | pn.Name()
                | pn.Char()
                | pn.Call()
            ):
                return pn.ToBool(node)
        throw_error(node)

    def _seperate_name_and_datatype(self, base_datatype, declarator):
        if isinstance(declarator, pn.Name):
            return base_datatype, declarator
        if isinstance(declarator, list):
            # Declarator fragment lists are expected to be non-empty and end in a name.
            *fragmented_datatypes, name = declarator
            full_datatype = base_datatype
            for fragmented_datatype in fragmented_datatypes:
                full_datatype = self._apply_declarator_fragment(
                    full_datatype, fragmented_datatype
                )
            return full_datatype, name
        throw_error(declarator)

    def _apply_declarator_fragment(self, base_datatype, fragmented_datatype):
        match fragmented_datatype:
            case pn.ArrayDecl(num, _):
                return pn.ArrayDecl(num, base_datatype)
            case pn.PntrDecl(_):
                return pn.PntrDecl(base_datatype)
            case pn.FunPtrDecl(_, params):
                return pn.FunPtrDecl(base_datatype, params)
            case _:
                throw_error(fragmented_datatype)

    # -------------------------------- General --------------------------------
    def translation_unit(self, _, children):
        return pn.File(pn.Name(global_vars.tstate.path_without_ext + ".ast"), children)

    def function_definition(self, _, children):
        storage_class_specifiers = _storage_class_specifiers(children)
        children = _without_storage_class_specifiers(children)
        base_datatype = children[0]
        declarator = children[1]
        match declarator:
            case pn.FunDecl(_, _, name, allocs):
                return pn.FunDef(storage_class_specifiers, base_datatype, name, allocs, children[2])
            case [*fragments, pn.FunDecl(_, _, name, allocs)]:
                datatype = base_datatype
                for fragment in fragments:
                    datatype = self._apply_declarator_fragment(datatype, fragment)
                # case pn.ArrayDecl(num, _) is not possible here: functions
                # cannot return arrays, only pointers to arrays/functions.
                if isinstance(datatype, pn.ArrayDecl):
                    throw_error(datatype)
                return pn.FunDef(storage_class_specifiers, datatype, name, allocs, children[2])
            case [pn.Name() as name, params]:
                return pn.FunDef(storage_class_specifiers, base_datatype, name, params, children[2])
        throw_error(declarator)

    def function_declarator(self, _, children):
        match children:
            case [pn.Name() as name, params]:
                return pn.FunDecl([], pn.Placeholder(), name, params)
            case [declarator, params]:
                self._reject_named_funptr_params(params)
                if not isinstance(declarator, list):
                    throw_error(declarator)
                match declarator:
                    case [pn.PntrDecl(_), *rest]:
                        return [pn.FunPtrDecl(pn.Placeholder(), params), *rest]
                    case _:
                        throw_error(
                            "Function pointer declarations must use '*', e.g. "
                            "int (*fp)(int);"
                        )
        return children

    def _reject_named_funptr_params(self, params):
        for param in params:
            match param:
                case pn.Alloc():
                    throw_error(
                        "Named parameters in function pointer declarations are not "
                        "supported; use unnamed parameter types instead, e.g. "
                        "'int (*fp)(int, char);' instead of "
                        "'int (*fp)(int x, char y);'"
                    )
                case pn.ParamDecl(_, datatype):
                    self._reject_named_funptr_params_in_datatype(datatype)
                case _:
                    pass

    def _reject_named_funptr_params_in_datatype(self, datatype):
        match datatype:
            case pn.ArrayDecl(_, inner_dt) | pn.PntrDecl(inner_dt):
                self._reject_named_funptr_params_in_datatype(inner_dt)
            case pn.FunPtrDecl(_, params):
                self._reject_named_funptr_params(params)
            case _:
                pass

    def identifier(self, node, _):
        return pn.Name(self.value(node))

    def primitive_type(self, node, _):
        match self.value(node):
            case "void":
                return pn.VoidType()
            case "int":
                return pn.IntType()
            case "char":
                return pn.CharType()
            case _:
                return pn.Error()

    def parameter_list(self, _, children):
        return children

    def variadic_parameter(self, _, children):
        if children:
            throw_error(children)
        return pn.VariadicParam()

    def parameter_declaration(self, _, children):
        match children:
            case [pn.VoidType() as void_type]:
                return void_type
            case [base_datatype]:
                return pn.ParamDecl(pn.Writeable(), base_datatype)
            case [pn.Const() as type_qual, base_datatype]:
                return pn.ParamDecl(type_qual, base_datatype)
            case [base_datatype, declarator]:
                type_qual = pn.Writeable()
            case [type_qual, base_datatype, declarator]:
                pass
            case _:
                throw_error(children)

        datatype, name = self._seperate_name_and_datatype(base_datatype, declarator)
        return pn.Alloc(type_qual, datatype, name)

    def compound_statement(self, _, children):
        return children

    def declaration(self, _, children):
        storage_class_specifiers = _storage_class_specifiers(children)
        children = _without_storage_class_specifiers(children)
        if len(children) == 2:
            type_qual = pn.Writeable()
            base_datatype, init_or_decl = children
        elif len(children) == 3:
            type_qual, base_datatype, init_or_decl = children
        else:
            throw_error(len(children))

        match init_or_decl:
            case pn.Assign(pn.Alloc(_, _, declarator), val):
                full_datatype, name = self._seperate_name_and_datatype(base_datatype, declarator)
                return pn.Assign(pn.Alloc(type_qual, full_datatype, name), val)
            case pn.FunDecl(_, pn.Placeholder(), pn.Name() as name, allocs):
                return pn.FunDecl(storage_class_specifiers, base_datatype, name, allocs)
            case [*fragments, pn.FunDecl(_, pn.Placeholder(), pn.Name() as name, allocs)]:
                full_datatype = base_datatype
                for fragment in fragments:
                    full_datatype = self._apply_declarator_fragment(
                        full_datatype, fragment
                    )
                # case pn.ArrayDecl(num, _) is not possible here: functions
                # cannot return arrays, only pointers to arrays/functions.
                if isinstance(full_datatype, pn.ArrayDecl):
                    throw_error(full_datatype)
                return pn.FunDecl(storage_class_specifiers, full_datatype, name, allocs)
            case [pn.FunPtrDecl() | pn.PntrDecl() | pn.ArrayDecl(), *_] | pn.Name():
                full_datatype, name = self._seperate_name_and_datatype(base_datatype, init_or_decl)
                return pn.Exp(pn.Alloc(type_qual, full_datatype, name))
        throw_error(init_or_decl)

    def type_qualifier(self, node, _):
        match self.value(node):
            case "const":
                return pn.Const()
            case _:
                throw_error(self.value(node))

    def storage_class_specifier(self, node, _):
        match self.value(node):
            case "inline":
                return pn.Inline()
            case "static":
                return pn.Static()
            case _:
                throw_error(self.value(node))

    def init_declarator(self, _, children):
        declarator, initializer = children
        return pn.Assign(
            pn.Alloc(pn.Placeholder(), pn.Placeholder(), declarator), initializer
        )

    def number_literal(self, node, _):
        return pn.Num(self.value(node))

    def char_literal(self, node, _):
        return pn.Char(self.value(node)[1:-1])

    def string_literal(self, node, _):
        literal = self.value(node)
        return pn.String(literal[1:-1])

    def parenthesized_expression(self, _, children):
        return children[0]

    def unary_expression(self, node, children):
        operand = children[0]
        op = self.operator(node)

        match op:
            case "-":
                return pn.UnOp(pn.Minus(), operand)
            case "+":
                return operand
            case "!":
                return pn.UnOp(pn.LogicNot(), self._to_bool(operand))
            case "~":
                return pn.UnOp(pn.Not(), operand)
        throw_error(f"Unsupported unary operator '{op}'")

    def binary_expression(self, node, children):
        if len(children) != 2:
            throw_error(f"Expected 2 operands for binary_expression, got {len(children)}")

        left, right = children
        op = self.operator(node)
        bin_node = self._bin_op(op)

        if isinstance(bin_node, (pn.Lt, pn.LtE, pn.Gt, pn.GtE, pn.Eq, pn.NEq)):
            return pn.Atom(left, bin_node, right)
        if isinstance(bin_node, (pn.LogicAnd, pn.LogicOr)):
            return pn.BinOp(self._to_bool(left), bin_node, self._to_bool(right))
        return pn.BinOp(left, bin_node, right)

    def update_expression(self, node, children):
        operand = children[0]
        op = self.operator(node)

        match op:
            case "++":
                return pn.PostInc(operand)
            case "--":
                return pn.PostDec(operand)
        throw_error(f"Unsupported update operator '{op}'")

    def expression_statement(self, _, children):
        match children[0]:
            case pn.Assign():
                return children[0]
        return pn.Exp(children[0])

    def assignment_expression(self, _, children):
        lhs, rhs = children
        return pn.Assign(lhs, rhs)
    
    # --------------------------------- Loops ---------------------------------
    def do_statement(self, _, children):
        return pn.DoWhile(children[1], children[0])

    def while_statement(self, _, children):
        return pn.While(children[0], children[1])

    # ------------------------------- Functions -------------------------------
    def call_expression(self, _, children):
        return pn.Call(children[0], children[1])
        
    def argument_list(self, _, children):
        return children

    def return_statement(self, _, children):
        if not children:
            return pn.Return(pn.Empty())
        return pn.Return(children[0])

    def gnu_asm_expression(self, node, children):
        if len(children) != 1:
            throw_error(
                f"Only asm with a single string literal is supported, got {self.value(node)}"
            )
        return pn.Asm(children[0])

    # --------------------------------- Array ---------------------------------
    def array_declarator(self, _, children):
        match children:
            case [declarator, size]:
                pass
            case [declarator]:
                size = pn.Empty()
            case _:
                throw_error(children)
        base = declarator if isinstance(declarator, list) else [declarator]
        return [pn.ArrayDecl(size, pn.Placeholder()), *base]

    def pointer_declarator(self, _, children):
        declarator = children[0]
        base = declarator if isinstance(declarator, list) else [declarator]
        return [pn.PntrDecl(pn.Placeholder()), *base]

    def initializer_list(self, _, children):
        """
        Distinguish struct-style initializer pairs from array/aggregate expressions.
        """
        if children and isinstance(children[0], pn.InitPair):
            return pn.Struct(children)
        return pn.Array(children)

    def debug_statement(self, *_):
        return pn.Debug()
        
    def initializer_pair(self, _, children):
        return pn.InitPair(children[0], children[1])

    def field_designator(self, _, children):
        return children[0]

    def field_identifier(self, node, _):
        return pn.Name(self.value(node))

    # -------------------------------- Struct ---------------------------------
    def struct_specifier(self, _, children):
        if len(children) == 1:
            return pn.StructSpec(children[0])
        return pn.StructDecl(children[0], children[1])

    def type_identifier(self, node, _):
        return pn.Name(self.value(node))

    def field_declaration_list(self, _, children):
        return children

    def subscript_expression(self, _, children):
        return pn.Subscr(children[0], children[1])

    def field_expression(self, node, children):
        op = self.operator(node)
        base = children[0]
        if op == "->":
            match base:
                case pn.BinOp():
                    pass
                case _:
                    base = pn.BinOp(base, pn.Add(), pn.Num("0"))
            base = pn.Deref(base)
        elif op != ".":
            throw_error(op)
        return pn.Attr(base, children[1])

    def pointer_expression(self, node, children):
        op = self.operator(node)
        match op:
            case "*":
                inner_exp = children[0]
                match inner_exp:
                    case pn.BinOp():
                        pass
                    case _:
                        inner_exp = pn.BinOp(inner_exp, pn.Add(), pn.Num("0"))
                return pn.Deref(inner_exp)
            case "&":
                return pn.Ref(children[0])
        throw_error(op)

    def field_declaration(self, _, children):
        if len(children) == 2:
            type_qual = pn.Writeable()
            base_datatype, declarator = children
        elif len(children) == 3:
            type_qual, base_datatype, declarator = children
        else:
            throw_error(len(children))

        datatype, name = self._seperate_name_and_datatype(base_datatype, declarator)
        return pn.Alloc(type_qual, datatype, name)

    # ------------------------------- L_If_Else -------------------------------

    def if_statement(self, _, children):
        match children:
            case [exp, then_branch]:
                then_stmts = then_branch if isinstance(then_branch, list) else [then_branch]
                return pn.If(self._to_bool(exp), then_stmts)
            case [exp, then_branch, else_branch]:
                then_stmts = then_branch if isinstance(then_branch, list) else [then_branch]
                else_stmts = else_branch if isinstance(else_branch, list) else [else_branch]
                return pn.IfElse(self._to_bool(exp), then_stmts, else_stmts)
        throw_error(children)

    def else_clause(self, _, children):
        return children[0]

    # HERE start
    def sizeof_expression(self, _, children):
        return pn.SizeOf(children[0])

    def cast_expression(self, _, children):
        datatype, exp = children
        return pn.Cast(datatype, exp)

    def type_descriptor(self, _, children):
        base_datatype = children[0]
        pointer_depth = children[1] if len(children) > 1 else 0
        for _ in range(pointer_depth):
            base_datatype = pn.PntrDecl(base_datatype)
        return base_datatype

    def abstract_pointer_declarator(self, node, _):
        return len(self._unnamed_children(node))


# ============================================================================
# =                           RETI Blocks Roundtrip                          =
# ============================================================================
# The `reti_blocks` pass stores linker-relevant block attributes inside
# assembler directives below each block label. When several `.reti_blocks`
# files are linked later, these directives allow the compiler to reconstruct
# `Block(...)` nodes with stable metadata such as scope, block indices, layout
# information, and any additional linker annotations that should survive the
# textual assembly form.


@dataclass(slots=True)
class _RetiDirective:
    name: str
    arguments: list[object]


class TransformerRetiBlocks(_TreeSitterTransformer):
    """
    Tree-sitter backed transformer that rebuilds a `.reti_blocks` file into
    the block-based AST shape used by later RETI passes.
    """

    _REGISTER_TYPES = {
        "ACC": rn.Acc,
        "IN1": rn.In1,
        "IN2": rn.In2,
        "PC": rn.Pc,
        "SP": rn.Sp,
        "BAF": rn.Baf,
        "CS": rn.Cs,
        "DS": rn.Ds,
    }

    _RELATION_TYPES = {
        "<": rn.Lt,
        "<=": rn.LtE,
        ">": rn.Gt,
        ">=": rn.GtE,
        "==": rn.Eq,
        "!=": rn.NEq,
        "_NOP": rn.NOp,
    }

    _REGISTER_ARGUMENT_OPS = {
        "ADD": rn.Add,
        "SUB": rn.Sub,
        "MULT": rn.Mult,
        "DIV": rn.Div,
        "MOD": rn.Mod,
        "OPLUS": rn.Oplus,
        "OR": rn.Or,
        "AND": rn.And,
    }

    _REGISTER_IMMEDIATE_OPS = {
        "ADDI": rn.Addi,
        "SUBI": rn.Subi,
        "MULTI": rn.Multi,
        "DIVI": rn.Divi,
        "MODI": rn.Modi,
        "OPLUSI": rn.Oplusi,
        "ORI": rn.Ori,
        "ANDI": rn.Andi,
        "LOAD": rn.Load,
        "LOADI": rn.Loadi,
        "STORE": rn.Store,
    }

    _INDEXED_MEMORY_OPS = {
        "LOADIN": rn.Loadin,
        "STOREIN": rn.Storein,
        "TSL": rn.Tsl,
    }

    _BLOCK_ATTR_DIRECTIVES = {
        ".scope": "scope",
        ".instrs_before": "instrs_before",
        ".num_instrs": "num_instrs",
        ".block_idx": "block_idx",
        ".param_size": "param_size",
        ".local_vars_size": "local_vars_size",
    }

    def __init__(self):
        super().__init__(_load_reti_ts_language())

    def build_ast(self, tree, code: str):
        """
        Build the RETI blocks AST from a Tree-sitter parse tree.
        """
        return super().build_ast(tree, code)

    def _register(self, reg_name: str) -> rn.Reg:
        reg_type = self._REGISTER_TYPES.get(reg_name)
        if reg_type is None:
            throw_error(reg_name)
        return rn.Reg(reg_type())

    def _op_from_text(self, op_text: str):
        match op_text:
            case "+":
                return rn.Add()
            case "-":
                return rn.Sub()
        throw_error(op_text)

    def _coerce_numeric_attr(self, value):
        match value:
            case rn.Im(val):
                return pn.Num(str(val))
            case _:
                throw_error(value)

    def _directive_value(self, value):
        match value:
            case rn.Im(val):
                return str(val)
            case rn.Name(val):
                return val
            case rn.BinOp() | rn.Reg():
                return value
            case str():
                return value
            case _:
                throw_error(value)

    def _apply_block_directive(self, block: pn.Block, directive: _RetiDirective):
        attr_name = self._BLOCK_ATTR_DIRECTIVES.get(directive.name)
        if attr_name is None:
            return

        if len(directive.arguments) != 1:
            throw_error(directive)

        value = directive.arguments[0]
        match attr_name:
            case "scope":
                block.scope = self._directive_value(value)
            case "instrs_before" | "num_instrs":
                setattr(block, attr_name, self._coerce_numeric_attr(value))
            case "block_idx" | "param_size" | "local_vars_size":
                match value:
                    case rn.Im(val):
                        setattr(block, attr_name, int(val))
                    case _:
                        throw_error(value)
            case _:
                throw_error(attr_name)

    # ------------------------------- Structure ------------------------------
    def source_file(self, _, children):
        file_name = pn.Name(global_vars.tstate.path_without_ext + ".reti_blocks")
        items = children
        if children and isinstance(children[0], pn.Name) and children[0].val.endswith(".reti"):
            file_name = children[0]
            items = children[1:]

        output_items = []
        top_level_directives: dict[str, list[list[object]]] = {}
        top_level_statements = []
        for item in items:
            match item:
                case []:
                    continue
                case pn.Block() | pn.Section():
                    output_items.append(item)
                case _RetiDirective(name, arguments):
                    top_level_directives.setdefault(name, []).append(arguments)
                case _:
                    output_items.append(item)
                    top_level_statements.append(item)

        file_node = pn.File(file_name, output_items)
        file_node.assembler_directives = top_level_directives
        file_node.top_level_statements = top_level_statements
        return file_node

    def section(self, _, children):
        section_name, *entries = children
        return pn.Section(section_name, [entry for entry in entries if entry != []])

    def section_name(self, node, _):
        return self.value(node)

    def filename(self, node, _):
        return pn.Name(self.value(node))

    def label(self, node, _):
        return pn.Name(self.value(node))

    def block(self, _, children):
        label, *entries = children
        instructions = []
        directives = []
        for entry in entries:
            if entry == []:
                continue
            if isinstance(entry, _RetiDirective):
                directives.append(entry)
            else:
                instructions.append(entry)

        block = pn.Block(label.val, instructions)
        block.scope = "global"
        block.block_idx = -1
        block.assembler_directives = {}
        for directive in directives:
            block.assembler_directives.setdefault(directive.name, []).append(
                directive.arguments
            )
        for directive in directives:
            self._apply_block_directive(block, directive)
        return block

    # ------------------------------- Terminals ------------------------------
    def comment(self, node, _):
        raw = self.value(node)[1:].strip()
        if raw.startswith("//"):
            content = raw[2:].strip()
            return pn.SingleLineComment("# //", content)
        return pn.SingleLineComment("#", raw)

    def immediate(self, node, _):
        return rn.Im(self.value(node))

    def data_value(self, _, children):
        return children[0]

    def string(self, node, _):
        return self.value(node)[1:-1]

    def symbol(self, node, _):
        return rn.Name(self.value(node))

    def register(self, node, _):
        return self._register(self.value(node))

    # ------------------------------- Operands -------------------------------
    def symbol_offset(self, node, children):
        base, offset = children
        op_text = self.operator(node)
        match offset:
            case rn.Im(val):
                return rn.BinOp(base, self._op_from_text(op_text), int(val))
            case _:
                throw_error(offset)

    def symbolic_operand(self, _, children):
        return children[0]

    def argument(self, _, children):
        return children[0]

    def relation(self, node, _):
        relation_type = self._RELATION_TYPES.get(self.value(node))
        if relation_type is None:
            throw_error(self.value(node))
        return relation_type()

    # ------------------------------ Directives ------------------------------
    def directive_name(self, node, _):
        return self.value(node)

    def directive_argument(self, _, children):
        return children[0]

    def directive(self, _, children):
        return _RetiDirective(children[0], children[1:])

    # ----------------------------- Instructions -----------------------------
    def register_argument_opcode(self, node, _):
        op_type = self._REGISTER_ARGUMENT_OPS.get(self.value(node))
        if op_type is None:
            throw_error(self.value(node))
        return op_type()

    def register_immediate_opcode(self, node, _):
        op_type = self._REGISTER_IMMEDIATE_OPS.get(self.value(node))
        if op_type is None:
            throw_error(self.value(node))
        return op_type()

    def load_immediate_opcode(self, node, _):
        return self.value(node)

    def indexed_memory_opcode(self, node, _):
        op_type = self._INDEXED_MEMORY_OPS.get(self.value(node))
        if op_type is None:
            throw_error(self.value(node))
        return op_type()

    def compute_register_instruction(self, _, children):
        return rn.Instr(children[0], children[1:])

    def compute_immediate_instruction(self, _, children):
        return rn.Instr(children[0], children[1:])

    def load_immediate_instruction(self, _, children):
        opcode_text = children[0]
        if opcode_text == "LOAD":
            return rn.Instr(rn.Load(), children[1:])
        if opcode_text == "LOADI":
            return rn.Instr(rn.Loadi(), children[1:])
        throw_error(opcode_text)

    def store_instruction(self, _, children):
        return rn.Instr(rn.Store(), children)

    def load_indexed_instruction(self, _, children):
        return rn.Instr(rn.Loadin(), children)

    def store_indexed_instruction(self, _, children):
        return rn.Instr(rn.Storein(), children)

    def tsl_instruction(self, _, children):
        return rn.Instr(rn.Tsl(), children)

    def register_argument_instruction(self, _, children):
        return self.compute_register_instruction(_, children)

    def register_immediate_instruction(self, _, children):
        return self.compute_immediate_instruction(_, children)

    def indexed_memory_instruction(self, _, children):
        return rn.Instr(children[0], children[1:])

    def move_instruction(self, _, children):
        return rn.Instr(rn.Move(), children)

    def interrupt_instruction(self, _, children):
        return rn.Int(children[0])

    def return_from_interrupt_instruction(self, _, children):
        if children:
            throw_error(children)
        return rn.Rti()

    # --------------------------------- Jumps --------------------------------
    def name_target(self, _, children):
        return pn.Name(children[0])

    def goto_target(self, _, children):
        return pn.GoTo(children[0])

    def jump_target(self, _, children):
        return children[0]

    def jump(self, _, children):
        if len(children) == 1:
            relation = rn.Always()
            target = children[0]
        elif len(children) == 2:
            relation, target = children
        else:
            throw_error(children)

        if not isinstance(target, (rn.Im, rn.Name, rn.BinOp, pn.GoTo)):
            throw_error(target)
        if not isinstance(relation, rn.Always) and isinstance(target, rn.Name):
            target = pn.GoTo(pn.Name(target.val))
        return rn.Jump(relation, target)
