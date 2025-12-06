from lark.visitors import Transformer
from lark.lexer import Token
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error
from src import global_vars
from tree_sitter import Language, Parser
import tree_sitter_c
from typing import Sequence


_TS_LANGUAGE = Language(tree_sitter_c.language())


class TransformerPicoC:
    """
    Tree-sitter backed transformer that builds the PicoC AST using the
    upstream C grammar.
    """

    def __init__(self):
        self.parser = Parser()
        self.parser.language = _TS_LANGUAGE
        # Dispatch maps for fast, explicit node handling. Handler names mirror
        # the upstream tree-sitter C grammar rules in ../vendor/tree-sitter-c/grammar.js.
        self._tu_dispatch = {
            "function_definition": self.function_definition,
            "declaration": self.declaration,
        }
        self._stmt_dispatch = {
            "declaration": self.declaration,
            "expression_statement": self.expression_statement,
            "return_statement": self.return_statement,
            "if_statement": self.if_statement,
            "while_statement": self.while_statement,
            "do_statement": self.do_statement,
            "compound_statement": self.compound_statement,
            "break_statement": self.break_statement,
        }
        self._expr_dispatch = {
            "identifier": self.identifier,
            "number_literal": self.number_literal,
            "char_literal": self.char_literal,
            "string_literal": self.string_literal,
            "parenthesized_expression": self.parenthesized_expression,
            "call_expression": self.call_expression,
            "binary_expression": self.binary_expression,
            "assignment_expression": self.assignment_expression,
            "unary_expression": self.unary_expression,
            "pointer_expression": self.pointer_expression,
            "sizeof_expression": self.sizeof_expression,
            "subscript_expression": self.subscript_expression,
            "field_expression": self.field_expression,
            "initializer_list": self.initializer_list,
        }
        self._decl_node_dispatch = {
            "init_declarator": self.init_declarator,
            "function_declarator": self.function_declarator_node,
            "pointer_declarator": self.pointer_declarator_node,
            "array_declarator": self.array_declarator_node,
            "parenthesized_declarator": self.parenthesized_declarator_node,
            "identifier": self.identifier_declarator_node,
        }
        self._declarator_dispatch = {
            "identifier": self.identifier_declarator,
            "parenthesized_declarator": self.parenthesized_declarator,
            "pointer_declarator": self.pointer_declarator,
            "array_declarator": self.array_declarator,
            "function_declarator": self.function_declarator,
        }

    # ------------------------------------------------------------------ public
    def parse_tree(self, code: str):
        return self.parser.parse(code.encode("utf-8"))

    def transform(self, code: str):
        tree = self.parse_tree(code)
        ast = self.translation_unit(tree.root_node, code)
        return tree, ast

    # ----------------------------------------------------------------- helpers
    def _text(self, node, code: str) -> str:
        return code[node.start_byte : node.end_byte]

    def _prim_type(self, node, code: str):
        text = self._text(node, code)
        match text:
            case "int":
                return pn.IntType()
            case "char":
                return pn.CharType()
            case "void":
                return pn.VoidType()
        throw_error(text)

    def _bin_op_node(self, op: str):
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
            case "<":
                return pn.Lt()
            case "<=":
                return pn.LtE()
            case ">":
                return pn.Gt()
            case ">=":
                return pn.GtE()
            case "==":
                return pn.Eq()
            case "!=":
                return pn.NEq()
        throw_error(op)

    def _wrap_pointers(self, base_dt, count: int):
        datatype = base_dt
        for _ in range(count):
            datatype = pn.PntrDecl(pn.Num("1"), datatype)
        return datatype

    def _wrap_arrays(self, base_dt, dims: Sequence[pn.Num]):
        datatype = base_dt
        for dim in dims:
            datatype = pn.ArrayDecl([dim], datatype)
        return datatype

    # ----------------------------------------------------------------- parsing
    def translation_unit(self, node, code: str):
        decls_defs = []
        for child in node.children:
            if not child.is_named:
                continue
            handler = self._tu_dispatch.get(child.type)
            if handler:
                result = handler(child, code)
                if result is None:
                    continue
                if isinstance(result, list):
                    decls_defs.extend(result)
                else:
                    decls_defs.append(result)

        return pn.File(
            pn.Name(global_vars.tstate.path_without_ext + ".ast"), decls_defs
        )

    # ------------------------------ declarators ------------------------------
    def _apply_declarator(self, node, base_type, code: str):
        """
        Walks a declarator chain using dispatch handlers. Each handler unwraps
        one layer and returns the next node to examine.
        """
        current_type = base_type
        current_node = node

        while True:
            handler = self._declarator_dispatch.get(current_node.type)
            if handler is None:
                throw_error(current_node.type)
            next_node, current_type, name, done = handler(current_node, current_type, code)
            if done:
                return current_type, name
            current_node = next_node

    # declarator handlers -----------------------------------------------------
    def identifier_declarator(self, node, current_type, code: str):
        return None, current_type, pn.Name(self._text(node, code)), True

    def parenthesized_declarator(self, node, current_type, code: str):
        inner = next(c for c in node.children if c.is_named)
        return inner, current_type, None, False

    def pointer_declarator(self, node, current_type, code: str):
        pointer_count = sum(
            1 for c in node.children if not c.is_named and self._text(c, code) == "*"
        )
        wrapped_type = self._wrap_pointers(current_type, pointer_count)
        inner = next(c for c in node.children if c.is_named)
        return inner, wrapped_type, None, False

    def array_declarator(self, node, current_type, code: str):
        size_node = node.child_by_field_name("size")
        dims = [pn.Num(self._text(size_node, code))] if size_node else []
        wrapped_type = self._wrap_arrays(current_type, dims)
        inner = node.child_by_field_name("declarator")
        return inner, wrapped_type, None, False

    def function_declarator(self, node, current_type, code: str):
        inner = node.child_by_field_name("declarator")
        return inner, current_type, None, False

    def parameter_declaration(self, node, code: str):
        type_node = node.child_by_field_name("type")
        dt = self._prim_type(type_node, code)
        declarator = node.child_by_field_name("declarator")
        datatype, name = self._apply_declarator(declarator, dt, code)
        return pn.Alloc(pn.Writeable(), datatype, name)

    def parameter_list(self, node, code: str):
        params = []
        for child in node.children:
            if child.type == "parameter_declaration":
                params.append(self.parameter_declaration(child, code))
        return params

    # ------------------------------ functions -------------------------------
    def function_definition(self, node, code: str):
        type_node = node.child_by_field_name("type")
        dt = self._prim_type(type_node, code)

        decl_node = node.child_by_field_name("declarator")
        params_node = decl_node.child_by_field_name("parameters")
        params = self.parameter_list(params_node, code) if params_node else []
        datatype, name = self._apply_declarator(
            decl_node.child_by_field_name("declarator"), dt, code
        )

        body_node = node.child_by_field_name("body")
        stmts = self.compound_statement(body_node, code)

        return pn.FunDef(datatype, name, params, stmts)

    # ----------------------------- declarations -----------------------------
    def declaration(self, node, code: str):
        type_node = node.child_by_field_name("type")
        if type_node is None:
            return []
        base_type = self._prim_type(type_node, code)
        results = []

        # Accept both wrapped (init_declarator) and bare declarator children.
        declarator_nodes = [child for child in node.children if child.is_named]
        if declarator_nodes and declarator_nodes[0] is type_node:
            declarator_nodes = declarator_nodes[1:]

        for child in declarator_nodes:
            handler = self._decl_node_dispatch.get(child.type)
            if handler:
                handler(child, base_type, code, results)

        return results

    # declaration handlers ----------------------------------------------------
    def init_declarator(self, child, base_type, code: str, results: list):
        declarator = child.child_by_field_name("declarator")
        value_node = child.child_by_field_name("value")
        self._decl_process(declarator, value_node, base_type, code, results)

    def function_declarator_node(self, child, base_type, code: str, results: list):
        self._decl_process(child, None, base_type, code, results)

    def pointer_declarator_node(self, child, base_type, code: str, results: list):
        self._decl_process(child, None, base_type, code, results)

    def array_declarator_node(self, child, base_type, code: str, results: list):
        self._decl_process(child, None, base_type, code, results)

    def parenthesized_declarator_node(self, child, base_type, code: str, results: list):
        self._decl_process(child, None, base_type, code, results)

    def identifier_declarator_node(self, child, base_type, code: str, results: list):
        self._decl_process(child, None, base_type, code, results)

    def _decl_process(self, declarator, value_node, base_type, code: str, results: list):
        if declarator.type == "function_declarator":
            params_node = declarator.child_by_field_name("parameters")
            params = self.parameter_list(params_node, code) if params_node else []
            datatype, name = self._apply_declarator(
                declarator.child_by_field_name("declarator"), base_type, code
            )
            results.append(pn.FunDecl(datatype, name, params))
            return

        datatype, name = self._apply_declarator(declarator, base_type, code)
        alloc = pn.Alloc(pn.Writeable(), datatype, name)
        if value_node:
            init_val = self.expression(value_node, code)
            results.append(pn.Assign(alloc, init_val))
        else:
            results.append(pn.Exp(alloc))

    # ------------------------------- statements -----------------------------
    def compound_statement(self, node, code: str):
        stmts = []
        for child in node.children:
            if not child.is_named:
                continue
            stmts.extend(self.statement(child, code))
        return stmts

    def statement(self, node, code: str):
        handler = self._stmt_dispatch.get(node.type)
        if handler is None:
            return []
        return handler(node, code)

    def expression_statement(self, node, code: str):
        expr_child = next((c for c in node.children if c.is_named), None)
        if expr_child is None:
            return []
        expr = self.expression(expr_child, code)
        if isinstance(expr, pn.Assign):
            return [expr]
        return [pn.Exp(expr)]

    def return_statement(self, node, code: str):
        expr_child = next((c for c in node.children if c.is_named), None)
        return [pn.Return(self.expression(expr_child, code) if expr_child else pn.Empty())]

    def if_statement(self, node, code: str):
        cond = self.expression(node.child_by_field_name("condition"), code)
        cons = self.statement(node.child_by_field_name("consequence"), code)
        alt_node = node.child_by_field_name("alternative")
        if alt_node:
            alt = self.statement(alt_node, code)
            return [pn.IfElse(cond, cons, alt)]
        return [pn.If(cond, cons)]

    def while_statement(self, node, code: str):
        cond = self.expression(node.child_by_field_name("condition"), code)
        body = self.statement(node.child_by_field_name("body"), code)
        return [pn.While(cond, body)]

    def do_statement(self, node, code: str):
        body = self.statement(node.child_by_field_name("body"), code)
        cond = self.expression(node.child_by_field_name("condition"), code)
        return [pn.DoWhile(cond, body)]

    def break_statement(self, node, code: str):
        return [pn.Exp(pn.Call(pn.Name("break"), []))]

    # ------------------------------- expressions ----------------------------
    def expression(self, node, code: str):
        if node is None:
            return pn.Empty()
        handler = self._expr_dispatch.get(node.type)
        if handler is None:
            throw_error(node.type)
        return handler(node, code)

    def identifier(self, node, code: str):
        return pn.Name(self._text(node, code))

    def number_literal(self, node, code: str):
        return pn.Num(self._text(node, code))

    def char_literal(self, node, code: str):
        literal = self._text(node, code)
        return pn.Char(literal[1:-1])

    def string_literal(self, node, code: str):
        return pn.Name(self._text(node, code))

    def parenthesized_expression(self, node, code: str):
        inner = next(c for c in node.children if c.is_named)
        return self.expression(inner, code)

    def call_expression(self, node, code: str):
        # call_expression -> function "(" arguments? ")"
        func = self.expression(node.child_by_field_name("function"), code)
        args_node = node.child_by_field_name("arguments")
        args = [
            self.expression(child, code)
            for child in args_node.children
            if child.is_named
        ] if args_node else []
        return pn.Call(func, args)

    def binary_expression(self, node, code: str):
        # binary_expression -> left operator right
        left = self.expression(node.child_by_field_name("left"), code)
        right = self.expression(node.child_by_field_name("right"), code)
        op = next(self._text(c, code) for c in node.children if not c.is_named)
        bin_node = self._bin_op_node(op)
        if isinstance(bin_node, (pn.Lt, pn.LtE, pn.Gt, pn.GtE, pn.Eq, pn.NEq)):
            return pn.Atom(left, bin_node, right)
        if isinstance(bin_node, (pn.LogicAnd, pn.LogicOr)):
            return pn.BinOp(self._to_bool(left), bin_node, self._to_bool(right))
        return pn.BinOp(left, bin_node, right)

    def assignment_expression(self, node, code: str):
        # assignment_expression -> left "=" right
        left = self.expression(node.child_by_field_name("left"), code)
        right = self.expression(node.child_by_field_name("right"), code)
        return pn.Assign(left, right)

    def unary_expression(self, node, code: str):
        # unary_expression -> ("-" | "!" | "~") expression
        op = next(self._text(c, code) for c in node.children if not c.is_named)
        exp = self.expression(next(c for c in node.children if c.is_named), code)
        match op:
            case "-":
                return pn.UnOp(pn.Minus(), exp)
            case "!":
                return pn.UnOp(pn.LogicNot(), self._to_bool(exp))
            case "~":
                return pn.UnOp(pn.Not(), exp)
        throw_error(op)

    def pointer_expression(self, node, code: str):
        # pointer_expression -> ("&" | "*") expression
        op = self._text(next(c for c in node.children if not c.is_named), code)
        exp = self.expression(next(c for c in node.children if c.is_named), code)
        match op:
            case "&":
                return pn.Ref(exp)
            case "*":
                base, bin_op, rest = self._leftmost_node(exp)
                match bin_op:
                    case pn.Add():
                        return pn.Deref(base, rest)
                    case pn.Sub():
                        return pn.Deref(base, pn.UnOp(pn.Minus(), rest))
                    case None:
                        return pn.Deref(exp, pn.Num("0"))
        throw_error(op)

    def sizeof_expression(self, node, code: str):
        # sizeof_expression -> "sizeof" (type | value)
        target = node.child_by_field_name("type") or node.child_by_field_name("value")
        return pn.SizeOf(self.expression(target, code))

    def subscript_expression(self, node, code: str):
        # subscript_expression -> argument "[" index "]"
        base = self.expression(node.child_by_field_name("argument"), code)
        index = self.expression(node.child_by_field_name("index"), code)
        return pn.Subscr(base, index)

    def field_expression(self, node, code: str):
        # field_expression -> argument "." field
        argument = self.expression(node.child_by_field_name("argument"), code)
        field = node.child_by_field_name("field")
        return pn.Attr(argument, pn.Name(self._text(field, code)))

    def initializer_list(self, node, code: str):
        exps = [self.expression(c, code) for c in node.children if c.is_named]
        return pn.Array(exps)

    # ------------------------------ expression utils ------------------------
    def _leftmost_node(self, bin_exp):
        current_bin_exp = bin_exp
        previous_bin_exp = None
        match bin_exp:
            case pn.BinOp():
                pass
            case _:
                return bin_exp, None, None
        while isinstance(current_bin_exp.left_exp, pn.BinOp):
            match current_bin_exp:
                case pn.BinOp(exp1, _, _):
                    previous_bin_exp = current_bin_exp
                    current_bin_exp = exp1
        if current_bin_exp == bin_exp:
            match current_bin_exp:
                case pn.BinOp(exp1, bin_op, exp2):
                    return exp1, bin_op, exp2
        match current_bin_exp:
            case pn.BinOp(exp1, bin_op, exp2):
                previous_bin_exp.left_exp = exp2
                return exp1, bin_op, bin_exp
            case _:
                throw_error(current_bin_exp)

    def _to_bool(self, node):
        match node:
            case pn.BinOp(_, pn.LogicAnd(), _) | pn.BinOp(_, pn.LogicOr(), _) | pn.Atom():
                return node
            case pn.UnOp(pn.LogicNot(), _):
                return node
            case pn.BinOp():
                return pn.ToBool(node)
            case pn.UnOp():
                return pn.ToBool(node)
            case pn.Num() | pn.Name() | pn.Char():
                return pn.ToBool(node)
        throw_error(node)


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
