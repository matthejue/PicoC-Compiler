import ctypes
from pathlib import Path
from typing import Sequence

from lark.lexer import Token
from lark.visitors import Transformer
from tree_sitter import Language, Parser

from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error


def _load_ts_language() -> Language:
    """
    Load the vendored Tree-sitter C grammar (../vendor/tree-sitter-c/c.so)
    so local grammar changes are used instead of the PyPI wheel.
    """
    grammar_lib = (
        Path(__file__).resolve().parent.parent
        / "vendor"
        / "tree-sitter-c"
        / "c.so"
    )
    if not grammar_lib.exists():
        raise FileNotFoundError(
            f"Tree-sitter C grammar not found at {grammar_lib}. "
            "Build the grammar in vendor/tree-sitter-c."
        )
    lib = ctypes.CDLL(str(grammar_lib))
    if not hasattr(lib, "tree_sitter_c"):
        raise AttributeError(f"'tree_sitter_c' symbol missing in {grammar_lib}")
    lib.tree_sitter_c.restype = ctypes.c_void_p
    return Language(lib.tree_sitter_c())


_TS_LANGUAGE = _load_ts_language()


class TransformerPicoC:
    """
    Tree-sitter backed transformer that builds the PicoC AST using the
    vendored C grammar from ../vendor/tree-sitter-c.
    """

    def __init__(self):
        self.parser = Parser()
        self.parser.language = _TS_LANGUAGE
        self._code: str | None = None
        self._cache: dict[int, object] = {}

    def parse_tree(self, code: str):
        return self.parser.parse(code.encode("utf-8"))

    def build_ast(self, tree, code: str):
        """
        Build the PicoC AST from a Tree-sitter parse tree.
        """
        self._code = code
        return self.walk(tree.root_node)

    # -------------------------------- Helpers --------------------------------
    def value(self, node) -> str:
        return "" if self._code is None else self._code[node.start_byte : node.end_byte]

    def _named_children(self, node):
        return [c for c in node.children if c.is_named]

    def _unnamed_children(self, node):
        """Return all unnamed (token) children for a Tree-sitter node."""
        return [c for c in node.children if not c.is_named]

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
            case pn.BinOp() | pn.UnOp() | pn.Num() | pn.Name() | pn.Char():
                return pn.ToBool(node)
        throw_error(node)

    def operator(self, node):
        """
        Return the operator text from the first unnamed child of a node.
        Raises if no such child exists.
        """
        unnamed = self._unnamed_children(node)
        if not unnamed:
            throw_error(f"No unnamed children found in node '{node.type}'")
        return self.value(unnamed[0])

    def _field_children(self, node, children):
        """
        Returns a mapping of field_name -> list of child ASTs for quick lookup.
        """
        mapping: dict[str | None, list[object]] = {}
        field_names = [
            node.field_name_for_child(i)
            for i, child in enumerate(node.children)
            if child.is_named
        ]
        for field_name, child_ast in zip(field_names, children):
            mapping.setdefault(field_name, []).append(child_ast)
        return mapping

    def walk(self, root):
        """
        Iterative post-order walk that dispatches to methods named after
        Tree-sitter node types (e.g., `binary_expression`).
        """
        self._cache = {}
        stack = [(root, False)]
        while stack:
            node, done = stack.pop()
            if done:
                child_nodes = self._named_children(node)
                child_vals = [self._cache[id(c)] for c in child_nodes]
                handler = getattr(self, node.type, self.generic)
                self._cache[id(node)] = handler(node, child_vals)
            else:
                stack.append((node, True))
                for child in reversed(self._named_children(node)):
                    stack.append((child, False))
        return self._cache[id(root)]

    def generic(self, _node, children):
        if len(children) == 1:
            return children[0]
        return children

    # -------------------------------- General --------------------------------
    def translation_unit(self, _, children):
        return pn.File(pn.Name(global_vars.tstate.path_without_ext + ".ast"), children)

    def function_definition(self, _, children):
        return pn.FunDef(children[0], children[1][0], children[1][1], children[2])

    def function_declarator(self, _, children):
        return children

    def identifier(self, node, _):
        return pn.Name(self.value(node))

    def primitive_type(self, node, _):
        match self.value(node):
            case "void":
                return pn.VoidType()
            case "int":
                return pn.IntType()
        return

    def parameter_list(self, _, children):
        return children

    def compound_statement(self, _, children):
        return children

    def declaration(self, _, children):
        if len(children) == 2:
            match children[1]:
                case pn.Assign(pn.Alloc(_, _, identifier), val):
                    return pn.Assign(pn.Alloc(pn.Writeable(), children[0], identifier), val)
                case _:
                    throw_error(children[1])
        elif len(children == 3):
            match children[2]:
                case pn.Assign(pn.Alloc(_, _, identifier), val):
                    return pn.Assign(pn.Alloc(children[0], children[1], identifier), val)
                case _:
                    throw_error(children[2])
        else:
            throw_error(len(children))

    def type_qualifier(self, node, _):
        match self.value(node):
            case "const":
                return pn.Const()
            case _:
                throw_error(self.value(node))

    def init_declarator(self, _, children):
        return pn.Assign(
            pn.Alloc(pn.Placeholder(), pn.Placeholder(), children[0]), children[1]
        )

    def number_literal(self, node, _):
        return pn.Num(self.value(node))

    def parenthesized_expression(self, _, children):
        return children

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

    def expression_statement(self, _, children):
        return pn.Exp(children[0])
    
    # --------------------------------- Loops ---------------------------------
    def do_statement(self, _, children):
        return pn.DoWhile(children[0], children[1])

    # ------------------------------- Functions -------------------------------
    def call_expression(self, _, children):
        return pn.Call(children[0], children[1])
        
    def argument_list(self, _, children):
        return children

    # --------------------------------- Array ---------------------------------
    def array_declarator(self, _, children):
        match children[0]:
            case pn.ArrayDecl(nums, datatype):
                return pn.ArrayDecl([children[1]] + nums, datatype)
            case _:
                return pn.ArrayDecl([children[1]], children[0])

    def initializer_list(self, _, children):
        match children[0]:
            case pn.Assign():
                return pn.Struct(children)
            case pn.Num():
                return pn.Array(children)
            case _:
                return pn.Error()

    def debug_statement(self, *_):
        return pn.Debug()
        
    def initializer_pair(self, _, children):
        return pn.Assign(children[0], children[1])

    def field_designator(self, _, children):
        return children[0]

    def field_identifier(self, node, _):
        return pn.Name(self.value(node))

    # -------------------------------- Struct ---------------------------------
    def struct_specifier(self, _, children):
        if len(children) == 1:
            return pn.StructSpec(children[0])
        match children[1][0]:
            case pn.Alloc():
                return pn.StructDecl(children[0], children[1])
            case _:
                return pn.StructDecl(children[0], children[1])

    def type_identifier(self, node, _):
        return pn.Name(self.value(node))

    def field_declaration_list(self, _, children):
        return children

    def field_declaration(self, _, children):
        if len(children) == 2:
            return pn.Alloc(pn.Writeable(), children[0], children[1])
        # elif len(children) == 3:
        #     return pn.Alloc(children[0], children[1], children[2])
        else:
            throw_error(len(children))
        
    # HERE START
    # HERE END

class ASTTransformerRETI(Transformer):
    # =========================================================================
    # =                                 Lexer                                 =
    # =========================================================================
    # ------------------------------- L_Program -------------------------------
    def IM(self, token: Token):
        return rn.Im(token.value)

    def FILENAME(self, token: Token):
        return pn.Name(token.value)

    def NAME(self, token: Token):
        return pn.Name(token.value)

    def reg(self, tokens: list[Token]):
        token = tokens[0]
        match token.value:
            case "ACC":
                return rn.Reg(
                    rn.Acc(
                        token.value,
                    )
                )
            case "IN1":
                return rn.Reg(
                    rn.In1(
                        token.value,
                    )
                )
            case "IN2":
                return rn.Reg(
                    rn.In2(
                        token.value,
                    )
                )
            case "PC":
                return rn.Reg(
                    rn.Pc(
                        token.value,
                    )
                )
            case "SP":
                return rn.Reg(
                    rn.Sp(
                        token.value,
                    )
                )
            case "BAF":
                return rn.Reg(
                    rn.Baf(
                        token.value,
                    )
                )
            case "CS":
                return rn.Reg(
                    rn.Cs(
                        token.value,
                    )
                )
            case "DS":
                return rn.Reg(
                    rn.Ds(
                        token.value,
                    )
                )

    def arg(self, nodes_tokens):
        return nodes_tokens[0]

    def rel(self, tokens: list[Token]):
        token = tokens[0]
        match token.value:
            case "<":
                return rn.Lt(
                    token.value,
                )
            case "<=":
                return rn.LtE(
                    token.value,
                )
            case ">":
                return rn.Gt(
                    token.value,
                )
            case ">=":
                return rn.GtE(
                    token.value,
                )
            case "==":
                return rn.Eq(
                    token.value,
                )
            case "!=":
                return rn.NEq(
                    token.value,
                )
            case "_NOP":
                return rn.NOp(
                    token.value,
                )

    def ADD(self, token: Token):
        return rn.Add(token.value)

    def ADDI(self, token: Token):
        return rn.Addi(token.value)

    def SUB(self, token: Token):
        return rn.Sub(token.value)

    def SUBI(self, token: Token):
        return rn.Subi(token.value)

    def MULT(self, token: Token):
        return rn.Mult(token.value)

    def MULTI(self, token: Token):
        return rn.Multi(token.value)

    def DIV(self, token: Token):
        return rn.Div(token.value)

    def DIVI(self, token: Token):
        return rn.Divi(token.value)

    def MOD(self, token: Token):
        return rn.Mod(token.value)

    def MODI(self, token: Token):
        return rn.Modi(token.value)

    def OPLUS(self, token: Token):
        return rn.Oplus(token.value)

    def OPLUSI(self, token: Token):
        return rn.Oplusi(token.value)

    def OR(self, token: Token):
        return rn.Or(token.value)

    def ORI(self, token: Token):
        return rn.Ori(token.value)

    def AND(self, token: Token):
        return rn.And(token.value)

    def ANDI(self, token: Token):
        return rn.Andi(token.value)

    def LOAD(self, token: Token):
        return rn.Load(token.value)

    def LOADIN(self, token: Token):
        return rn.Loadin(token.value)

    def LOADI(self, token: Token):
        return rn.Loadi(token.value)

    def STORE(self, token: Token):
        return rn.Store(token.value)

    def STOREIN(self, token: Token):
        return rn.Storein(token.value)

    def MOVE(self, token: Token):
        return rn.Move(token.value)

    def INT(self, token: Token):
        return rn.Int(token.value)

    def RTI(self, token: Token):
        return rn.Rti(token.value)

    # =========================================================================
    # =                                 Parser                                =
    # =========================================================================
    # ------------------------------- L_Program -------------------------------
    def instr(self, nodes):
        return rn.Instr(nodes[0], nodes[1:])

    def jump(self, nodes):
        if len(nodes) == 1:
            return rn.Jump(rn.Always(), nodes[0])
        else:  # len(nodes) == 2:
            return rn.Jump(nodes[0], nodes[1])

    def call(self, nodes):
        return rn.Call(nodes[0], nodes[1])

    def program(self, nodes):
        nodes[0].val = global_vars.tstate.path_without_ext + ".rast"
        return rn.Program(nodes[0], nodes[1:])
