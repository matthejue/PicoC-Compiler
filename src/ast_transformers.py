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

    # ------------------------------------------------------------------ public
    def parse_tree(self, code: str):
        return self.parser.parse(code.encode("utf-8"))

    #
    # def transform(self, code: str):
    #     """
    #     Convenience helper: parse and build the AST in one step.
    #     """
    #     tree = self.parse_tree(code)
    #     ast = self.build_ast(tree, code)
    #     return tree, ast

    def build_ast(self, tree, code: str):
        """
        Build the PicoC AST from a Tree-sitter parse tree.
        """
        self._code = code
        return self.walk(tree.root_node)

    # ----------------------------------------------------------------- helpers
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

    # -------------------------------- parsing --------------------------------
    def translation_unit(self, _, children):
        return pn.File(pn.Name(global_vars.tstate.path_without_ext + ".ast"), children)

    def function_definition(self, _, children):
        return pn.FunDef(children[0], children[1][0], children[1][1], children[2])

    def function_declarator(self, _, children):
        return children

    def identifier(self, node, _):
        return pn.Name(self.value(node))

    def parameter_list(self, _, children):
        return children

    def primitive_type(self, node, _):
        match self.value(node):
            case "void":
                return pn.VoidType()
            case "int":
                return pn.IntType()
        return

    def compound_statement(self, _, children):
        return children

    def declaration(self, _, children):
        if len(children) == 2:
            match children[1]:
                case pn.Assign(pn.Alloc(_, _, identifier), val):
                    return pn.Assign(pn.Alloc(pn.Writeable(), children[0], identifier), val)
                case _:
                    throw_error(children[1])
        else:
            match children[2]:
                case pn.Assign(pn.Alloc(_, _, identifier), val):
                    return pn.Assign(pn.Alloc(children[0], children[1], identifier), val)
                case _:
                    throw_error(children[2])

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
        return pn.Array(children)

    def debug_statement(self, *_):
        return pn.Debug()
        
    # # ------------------------------ declarators ------------------------------
    # def _apply_declarator(self, node, base_type):
    #     """
    #     Walks a declarator chain using rule-specific handlers. Each handler
    #     unwraps one layer and returns the next node to examine.
    #     """
    #     current_type = base_type
    #     current_node = node
    #
    #     while True:
    #         match current_node.type:
    #             case "identifier":
    #                 next_node, current_type, name, done = self._identifier_declarator(
    #                     current_node, current_type
    #                 )
    #             case "parenthesized_declarator":
    #                 next_node, current_type, name, done = self._parenthesized_declarator(
    #                     current_node, current_type
    #                 )
    #             case "pointer_declarator":
    #                 next_node, current_type, name, done = self._pointer_declarator(
    #                     current_node, current_type
    #                 )
    #             case "array_declarator":
    #                 next_node, current_type, name, done = self._array_declarator(
    #                     current_node, current_type
    #                 )
    #             case "function_declarator":
    #                 next_node, current_type, name, done = self._function_declarator(
    #                     current_node, current_type
    #                 )
    #             case _:
    #                 throw_error(current_node.type)
    #         if done:
    #             return current_type, name
    #         current_node = next_node
    #
    # # declarator handlers -----------------------------------------------------
    # def _identifier_declarator(self, node, current_type):
    #     return None, current_type, pn.Name(self._text(node)), True
    #
    # def _parenthesized_declarator(self, node, current_type):
    #     inner = next(c for c in node.children if c.is_named)
    #     return inner, current_type, None, False
    #
    # def _pointer_declarator(self, node, current_type):
    #     pointer_count = sum(
    #         1 for c in node.children if not c.is_named and self._text(c) == "*"
    #     )
    #     wrapped_type = self._wrap_pointers(current_type, pointer_count)
    #     inner = next(c for c in node.children if c.is_named)
    #     return inner, wrapped_type, None, False
    #
    # def _array_declarator(self, node, current_type):
    #     size_node = node.child_by_field_name("size")
    #     dims = [pn.Num(self._text(size_node))] if size_node else []
    #     wrapped_type = self._wrap_arrays(current_type, dims)
    #     inner = node.child_by_field_name("declarator")
    #     return inner, wrapped_type, None, False
    #
    # def _function_declarator(self, node, current_type):
    #     inner = node.child_by_field_name("declarator")
    #     return inner, current_type, None, False
    #
    # def parameter_declaration(self, node, _children):
    #     type_node = node.child_by_field_name("type")
    #     dt = self._prim_type(type_node)
    #     declarator = node.child_by_field_name("declarator")
    #     datatype, name = self._apply_declarator(declarator, dt)
    #     return pn.Alloc(pn.Writeable(), datatype, name)
    #
    # def parameter_list(self, _node, children):
    #     return children
    #
    # # ------------------------------ functions -------------------------------
    # def function_definition(self, node, _children):
    #     type_node = node.child_by_field_name("type")
    #     dt = self._prim_type(type_node)
    #
    #     decl_node = node.child_by_field_name("declarator")
    #     params_node = decl_node.child_by_field_name("parameters")
    #     params = self._cache.get(id(params_node), []) if params_node else []
    #     datatype, name = self._apply_declarator(
    #         decl_node.child_by_field_name("declarator"), dt
    #     )
    #
    #     body_node = node.child_by_field_name("body")
    #     stmts = self._cache.get(id(body_node), [])
    #
    #     return pn.FunDef(datatype, name, params, stmts)
    #
    # # ----------------------------- declarations -----------------------------
    # def declaration(self, node, _children):
    #     type_node = node.child_by_field_name("type")
    #     if type_node is None:
    #         return []
    #     base_type = self._prim_type(type_node)
    #     results = []
    #
    #     # Accept both wrapped (init_declarator) and bare declarator children.
    #     declarator_nodes = [child for child in node.children if child.is_named]
    #     if declarator_nodes and declarator_nodes[0] is type_node:
    #         declarator_nodes = declarator_nodes[1:]
    #
    #     for child in declarator_nodes:
    #         match child.type:
    #             case "init_declarator":
    #                 self._init_declarator(child, base_type, results)
    #             case "function_declarator":
    #                 self._function_declarator_node(child, base_type, results)
    #             case "pointer_declarator":
    #                 self._pointer_declarator_node(child, base_type, results)
    #             case "array_declarator":
    #                 self._array_declarator_node(child, base_type, results)
    #             case "parenthesized_declarator":
    #                 self._parenthesized_declarator_node(child, base_type, results)
    #             case "identifier":
    #                 self._identifier_declarator_node(child, base_type, results)
    #             case _:
    #                 pass
    #
    #     return results
    #
    # # declaration handlers ----------------------------------------------------
    # def _init_declarator(self, child, base_type, results: list):
    #     declarator = child.child_by_field_name("declarator")
    #     value_node = child.child_by_field_name("value")
    #     self._decl_process(declarator, value_node, base_type, results)
    #
    # def _function_declarator_node(self, child, base_type, results: list):
    #     self._decl_process(child, None, base_type, results)
    #
    # def _pointer_declarator_node(self, child, base_type, results: list):
    #     self._decl_process(child, None, base_type, results)
    #
    # def _array_declarator_node(self, child, base_type, results: list):
    #     self._decl_process(child, None, base_type, results)
    #
    # def _parenthesized_declarator_node(self, child, base_type, results: list):
    #     self._decl_process(child, None, base_type, results)
    #
    # def _identifier_declarator_node(self, child, base_type, results: list):
    #     self._decl_process(child, None, base_type, results)
    #
    # def _decl_process(self, declarator, value_node, base_type, results: list):
    #     if declarator.type == "function_declarator":
    #         params_node = declarator.child_by_field_name("parameters")
    #         params = self._cache.get(id(params_node), []) if params_node else []
    #         datatype, name = self._apply_declarator(
    #             declarator.child_by_field_name("declarator"), base_type
    #         )
    #         results.append(pn.FunDecl(datatype, name, params))
    #         return
    #
    #     datatype, name = self._apply_declarator(declarator, base_type)
    #     alloc = pn.Alloc(pn.Writeable(), datatype, name)
    #     if value_node:
    #         init_val = self._cache.get(id(value_node), pn.Empty())
    #         results.append(pn.Assign(alloc, init_val))
    #     else:
    #         results.append(pn.Exp(alloc))
    #
    # # ------------------------------- statements -----------------------------
    # def compound_statement(self, _node, children):
    #     stmts = []
    #     for child in children:
    #         if isinstance(child, list):
    #             stmts.extend(child)
    #         else:
    #             stmts.append(child)
    #     return stmts
    #
    # def expression_statement(self, _node, children):
    #     if not children:
    #         return []
    #     expr = children[0]
    #     if isinstance(expr, pn.Assign):
    #         return [expr]
    #     return [pn.Exp(expr)]
    #
    # def return_statement(self, _node, children):
    #     expr_child = children[0] if children else pn.Empty()
    #     return [pn.Return(expr_child if children else pn.Empty())]
    #
    # def if_statement(self, node, children):
    #     fields = self._field_children(node, children)
    #     cond = fields.get("condition", [pn.Empty()])[0]
    #     cons = fields.get("consequence", [[]])[0]
    #     alt_list = fields.get("alternative")
    #     if alt_list:
    #         return [pn.IfElse(cond, cons, alt_list[0])]
    #     return [pn.If(cond, cons)]
    #
    # def while_statement(self, node, children):
    #     fields = self._field_children(node, children)
    #     cond = fields.get("condition", [pn.Empty()])[0]
    #     body = fields.get("body", [[]])[0]
    #     return [pn.While(cond, body)]
    #
    # def do_statement(self, node, children):
    #     fields = self._field_children(node, children)
    #     body = fields.get("body", [[]])[0]
    #     cond = fields.get("condition", [pn.Empty()])[0]
    #     return [pn.DoWhile(cond, body)]
    #
    # def break_statement(self, _node, _children):
    #     return [pn.Exp(pn.Call(pn.Name("break"), []))]
    #
    # # ------------------------------- expressions ----------------------------
    # def identifier(self, node, _children):
    #     return pn.Name(self._text(node))
    #
    # def number_literal(self, node, _children):
    #     return pn.Num(self._text(node))
    #
    # def char_literal(self, node, _children):
    #     literal = self._text(node)
    #     return pn.Char(literal[1:-1])
    #
    # def string_literal(self, node, _children):
    #     return pn.Name(self._text(node))
    #
    # def parenthesized_expression(self, _node, children):
    #     return children[0] if children else pn.Empty()
    #
    # def argument_list(self, _node, children):
    #     return children
    #
    # def call_expression(self, node, children):
    #     fields = self._field_children(node, children)
    #     func = fields.get("function", [pn.Empty()])[0]
    #     args = fields.get("arguments", [[]])[0] if fields.get("arguments") else []
    #     return pn.Call(func, args)
    #
    # def binary_expression(self, node, children):
    #     fields = self._field_children(node, children)
    #     left = fields.get("left", [pn.Empty()])[0]
    #     right = fields.get("right", [pn.Empty()])[0]
    #     op = next(self._text(c) for c in node.children if not c.is_named)
    #     bin_node = self._bin_op_node(op)
    #     if isinstance(bin_node, (pn.Lt, pn.LtE, pn.Gt, pn.GtE, pn.Eq, pn.NEq)):
    #         return pn.Atom(left, bin_node, right)
    #     if isinstance(bin_node, (pn.LogicAnd, pn.LogicOr)):
    #         return pn.BinOp(self._to_bool(left), bin_node, self._to_bool(right))
    #     return pn.BinOp(left, bin_node, right)
    #
    # def assignment_expression(self, node, children):
    #     # assignment_expression -> left "=" right
    #     fields = self._field_children(node, children)
    #     left = fields.get("left", [pn.Empty()])[0]
    #     right = fields.get("right", [pn.Empty()])[0]
    #     return pn.Assign(left, right)
    #
    # def unary_expression(self, node, children):
    #     # unary_expression -> ("-" | "!" | "~") expression
    #     op = next(self._text(c) for c in node.children if not c.is_named)
    #     exp = children[0] if children else pn.Empty()
    #     match op:
    #         case "-":
    #             return pn.UnOp(pn.Minus(), exp)
    #         case "!":
    #             return pn.UnOp(pn.LogicNot(), self._to_bool(exp))
    #         case "~":
    #             return pn.UnOp(pn.Not(), exp)
    #     throw_error(op)
    #
    # def pointer_expression(self, node, children):
    #     # pointer_expression -> ("&" | "*") expression
    #     op = self._text(next(c for c in node.children if not c.is_named))
    #     exp = children[0] if children else pn.Empty()
    #     match op:
    #         case "&":
    #             return pn.Ref(exp)
    #         case "*":
    #             base, bin_op, rest = self._leftmost_node(exp)
    #             match bin_op:
    #                 case pn.Add():
    #                     return pn.Deref(base, rest)
    #                 case pn.Sub():
    #                     return pn.Deref(base, pn.UnOp(pn.Minus(), rest))
    #                 case None:
    #                     return pn.Deref(exp, pn.Num("0"))
    #     throw_error(op)
    #
    # def sizeof_expression(self, node, children):
    #     # sizeof_expression -> "sizeof" (type | value)
    #     fields = self._field_children(node, children)
    #     targets = fields.get("type") or fields.get("value") or [pn.Empty()]
    #     return pn.SizeOf(targets[0])
    #
    # def subscript_expression(self, node, children):
    #     # subscript_expression -> argument "[" index "]"
    #     fields = self._field_children(node, children)
    #     base = fields.get("argument", [pn.Empty()])[0]
    #     index = fields.get("index", [pn.Empty()])[0]
    #     return pn.Subscr(base, index)
    #
    # def field_expression(self, node, children):
    #     # field_expression -> argument "." field
    #     fields = self._field_children(node, children)
    #     argument = fields.get("argument", [pn.Empty()])[0]
    #     named_indices = [i for i, ch in enumerate(node.children) if ch.is_named]
    #     field_nodes = [
    #         c
    #         for idx, c in enumerate(self._named_children(node))
    #         if node.field_name_for_child(named_indices[idx]) == "field"
    #     ]
    #     if field_nodes:
    #         return pn.Attr(argument, pn.Name(self._text(field_nodes[0])))
    #     throw_error(node)
    #
    # def initializer_list(self, _node, children):
    #     return pn.Array(children)
    #
    # # ------------------------------ expression utils ------------------------
    # def _leftmost_node(self, bin_exp):
    #     current_bin_exp = bin_exp
    #     previous_bin_exp = None
    #     match bin_exp:
    #         case pn.BinOp():
    #             pass
    #         case _:
    #             return bin_exp, None, None
    #     while isinstance(current_bin_exp.left_exp, pn.BinOp):
    #         match current_bin_exp:
    #             case pn.BinOp(exp1, _, _):
    #                 previous_bin_exp = current_bin_exp
    #                 current_bin_exp = exp1
    #     if current_bin_exp == bin_exp:
    #         match current_bin_exp:
    #             case pn.BinOp(exp1, bin_op, exp2):
    #                 return exp1, bin_op, exp2
    #     match current_bin_exp:
    #         case pn.BinOp(exp1, bin_op, exp2):
    #             previous_bin_exp.left_exp = exp2
    #             return exp1, bin_op, bin_exp
    #         case _:
    #             throw_error(current_bin_exp)
    #
    # def _to_bool(self, node):
    #     match node:
    #         case pn.BinOp(_, pn.LogicAnd(), _) | pn.BinOp(_, pn.LogicOr(), _) | pn.Atom():
    #             return node
    #         case pn.UnOp(pn.LogicNot(), _):
    #             return node
    #         case pn.BinOp():
    #             return pn.ToBool(node)
    #         case pn.UnOp():
    #             return pn.ToBool(node)
    #         case pn.Num() | pn.Name() | pn.Char():
    #             return pn.ToBool(node)
    #     throw_error(node)


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
