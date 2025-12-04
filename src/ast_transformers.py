from lark.visitors import Transformer
from lark.lexer import Token
import sys
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import remove_ext, nodes_to_str, throw_error
from src import global_vars
from tree_sitter import Language, Parser
import tree_sitter_c
from typing import Optional, Sequence


_TS_LANGUAGE = Language(tree_sitter_c.language())


class TransformerPicoC:
    """
    Tree-sitter backed transformer that builds the PicoC AST using the
    upstream C grammar.
    """

    def __init__(self):
        self.parser = Parser()
        self.parser.language = _TS_LANGUAGE

    # ------------------------------------------------------------------ public
    def parse_tree(self, code: str):
        return self.parser.parse(code.encode("utf-8"))

    def transform(self, code: str):
        tree = self.parse_tree(code)
        ast = self._translation_unit(tree.root_node, code)
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
    def _translation_unit(self, node, code: str):
        decls_defs = []
        for child in node.children:
            if not child.is_named:
                continue
            match child.type:
                case "function_definition":
                    decls_defs.append(self._function_definition(child, code))
                case "declaration":
                    decls_defs.extend(self._declaration(child, code))
                case _:
                    continue

        return pn.File(
            pn.Name(global_vars.tstate.path_without_ext + ".ast"), decls_defs
        )

    # ------------------------------ declarators ------------------------------
    def _apply_declarator(self, node, base_type, code: str):
        match node.type:
            case "identifier":
                return base_type, pn.Name(self._text(node, code))
            case "parenthesized_declarator":
                inner = next(c for c in node.children if c.is_named)
                return self._apply_declarator(inner, base_type, code)
            case "pointer_declarator":
                pointer_count = sum(1 for c in node.children if not c.is_named and self._text(c, code) == "*")
                inner = next(c for c in node.children if c.is_named)
                inner_type, name = self._apply_declarator(inner, base_type, code)
                return self._wrap_pointers(inner_type, pointer_count), name
            case "array_declarator":
                inner = node.child_by_field_name("declarator")
                size_node = node.child_by_field_name("size")
                dims = []
                if size_node:
                    dims.append(pn.Num(self._text(size_node, code)))
                inner_type, name = self._apply_declarator(inner, base_type, code)
                return self._wrap_arrays(inner_type, dims), name
            case "function_declarator":
                # We handle parameters separately when building FunDecl/FunDef
                inner = node.child_by_field_name("declarator")
                return self._apply_declarator(inner, base_type, code)
        throw_error(node.type)

    def _parameter_declaration(self, node, code: str):
        type_node = node.child_by_field_name("type")
        dt = self._prim_type(type_node, code)
        declarator = node.child_by_field_name("declarator")
        datatype, name = self._apply_declarator(declarator, dt, code)
        return pn.Alloc(pn.Writeable(), datatype, name)

    def _parameter_list(self, node, code: str):
        params = []
        for child in node.children:
            if child.type == "parameter_declaration":
                params.append(self._parameter_declaration(child, code))
        return params

    # ------------------------------ functions -------------------------------
    def _function_definition(self, node, code: str):
        type_node = node.child_by_field_name("type")
        dt = self._prim_type(type_node, code)

        decl_node = node.child_by_field_name("declarator")
        params_node = decl_node.child_by_field_name("parameters")
        params = self._parameter_list(params_node, code) if params_node else []
        datatype, name = self._apply_declarator(
            decl_node.child_by_field_name("declarator"), dt, code
        )

        body_node = node.child_by_field_name("body")
        stmts = self._compound_statement(body_node, code)

        return pn.FunDef(datatype, name, params, stmts)

    # ----------------------------- declarations -----------------------------
    def _declaration(self, node, code: str):
        type_node = node.child_by_field_name("type")
        if type_node is None:
            return []
        base_type = self._prim_type(type_node, code)
        results = []

        for child in node.children:
            if child.type != "init_declarator":
                continue
            declarator = child.child_by_field_name("declarator")
            value_node = child.child_by_field_name("value")

            if declarator.type == "function_declarator":
                params_node = declarator.child_by_field_name("parameters")
                params = self._parameter_list(params_node, code) if params_node else []
                datatype, name = self._apply_declarator(
                    declarator.child_by_field_name("declarator"), base_type, code
                )
                results.append(pn.FunDecl(datatype, name, params))
                continue

            datatype, name = self._apply_declarator(declarator, base_type, code)
            alloc = pn.Alloc(pn.Writeable(), datatype, name)
            if value_node:
                init_val = self._expression(value_node, code)
                results.append(pn.Assign(alloc, init_val))
            else:
                results.append(pn.Exp(alloc))

        return results

    # ------------------------------- statements -----------------------------
    def _compound_statement(self, node, code: str):
        stmts = []
        for child in node.children:
            if not child.is_named:
                continue
            stmts.extend(self._statement(child, code))
        return stmts

    def _statement(self, node, code: str):
        match node.type:
            case "declaration":
                return self._declaration(node, code)
            case "expression_statement":
                # empty statements return []
                expr_child = next((c for c in node.children if c.is_named), None)
                if expr_child is None:
                    return []
                expr = self._expression(expr_child, code)
                if isinstance(expr, pn.Assign):
                    return [expr]
                return [pn.Exp(expr)]
            case "return_statement":
                expr_child = next((c for c in node.children if c.is_named), None)
                return [pn.Return(self._expression(expr_child, code) if expr_child else pn.Empty())]
            case "if_statement":
                cond = self._expression(node.child_by_field_name("condition"), code)
                cons = self._statement(node.child_by_field_name("consequence"), code)
                alt_node = node.child_by_field_name("alternative")
                if alt_node:
                    alt = self._statement(alt_node, code)
                    return [pn.IfElse(cond, cons, alt)]
                return [pn.If(cond, cons)]
            case "while_statement":
                cond = self._expression(node.child_by_field_name("condition"), code)
                body = self._statement(node.child_by_field_name("body"), code)
                return [pn.While(cond, body)]
            case "do_statement":
                body = self._statement(node.child_by_field_name("body"), code)
                cond = self._expression(node.child_by_field_name("condition"), code)
                return [pn.DoWhile(cond, body)]
            case "compound_statement":
                return self._compound_statement(node, code)
            case "break_statement":
                return [pn.Exp(pn.Call(pn.Name("break"), []))]
        return []

    # ------------------------------- expressions ----------------------------
    def _expression(self, node, code: str):
        if node is None:
            return pn.Empty()

        match node.type:
            case "identifier":
                return pn.Name(self._text(node, code))
            case "number_literal":
                return pn.Num(self._text(node, code))
            case "char_literal":
                literal = self._text(node, code)
                return pn.Char(literal[1:-1])
            case "string_literal":
                return pn.Name(self._text(node, code))
            case "parenthesized_expression":
                inner = next(c for c in node.children if c.is_named)
                return self._expression(inner, code)
            case "call_expression":
                func = self._expression(node.child_by_field_name("function"), code)
                args_node = node.child_by_field_name("arguments")
                args = []
                if args_node:
                    for child in args_node.children:
                        if child.is_named:
                            args.append(self._expression(child, code))
                return pn.Call(func, args)
            case "binary_expression":
                left = self._expression(node.child_by_field_name("left"), code)
                right = self._expression(node.child_by_field_name("right"), code)
                op = next(self._text(c, code) for c in node.children if not c.is_named)
                bin_node = self._bin_op_node(op)
                if isinstance(bin_node, (pn.Lt, pn.LtE, pn.Gt, pn.GtE, pn.Eq, pn.NEq)):
                    return pn.Atom(left, bin_node, right)
                if isinstance(bin_node, (pn.LogicAnd, pn.LogicOr)):
                    return pn.BinOp(self._to_bool(left), bin_node, self._to_bool(right))
                return pn.BinOp(left, bin_node, right)
            case "assignment_expression":
                left = self._expression(node.child_by_field_name("left"), code)
                right = self._expression(node.child_by_field_name("right"), code)
                return pn.Assign(left, right)
            case "unary_expression":
                op = next(self._text(c, code) for c in node.children if not c.is_named)
                exp = self._expression(next(c for c in node.children if c.is_named), code)
                match op:
                    case "-":
                        return pn.UnOp(pn.Minus(), exp)
                    case "!":
                        return pn.UnOp(pn.LogicNot(), self._to_bool(exp))
                    case "~":
                        return pn.UnOp(pn.Not(), exp)
                throw_error(op)
            case "pointer_expression":
                op = self._text(next(c for c in node.children if not c.is_named), code)
                exp = self._expression(next(c for c in node.children if c.is_named), code)
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
                        throw_error(bin_op)
                throw_error(op)
            case "sizeof_expression":
                target = node.child_by_field_name("type") or node.child_by_field_name("value")
                return pn.SizeOf(self._expression(target, code))
            case "subscript_expression":
                base = self._expression(node.child_by_field_name("argument"), code)
                index = self._expression(node.child_by_field_name("index"), code)
                return pn.Subscr(base, index)
            case "field_expression":
                argument = self._expression(node.child_by_field_name("argument"), code)
                field = node.child_by_field_name("field")
                return pn.Attr(argument, pn.Name(self._text(field, code)))
            case "initializer_list":
                exps = [self._expression(c, code) for c in node.children if c.is_named]
                return pn.Array(exps)
        throw_error(node.type)

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
