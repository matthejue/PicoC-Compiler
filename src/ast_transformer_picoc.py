from lark.visitors import Transformer
from lark.lexer import Token
from picoc_nodes import N
from global_classes import Pos
from global_funs import bug_in_compiler
import global_vars


class ASTTransformerPicoC(Transformer):
    # =========================================================================
    # =                                 Lexer                                 =
    # =========================================================================
    # --------------------------------- L_Arith -------------------------------
    def name(self, token_list):
        token = token_list[0]
        return N.Name(token.value, Pos(token.line, token.column))

    def NUM(self, token: Token):
        return N.Num(token.value, Pos(token.line, token.column))

    def CHAR(self, token: Token):
        return N.Char(token.value, Pos(token.line, token.column))

    def un_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "-":
                return N.Minus(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "~":
                return N.Not(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "!":
                return N.LogicNot(
                    token.value,
                    Pos(token.line, token.column),
                )

    def prec1_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "*":
                return N.Mul(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "/":
                return N.Div(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "%":
                return N.Mod(
                    token.value,
                    Pos(token.line, token.column),
                )

    def prec2_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "+":
                return N.Add(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "-":
                return N.Sub(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "^":
                return N.Oplus(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "&":
                return N.And(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "|":
                return N.Or(
                    token.value,
                    Pos(token.line, token.column),
                )

    # --------------------------------- L_Logic -------------------------------
    def relation(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "==":
                return N.Eq(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "!=":
                return N.NEq(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "<":
                return N.Lt(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "<=":
                return N.LtE(
                    token.value,
                    Pos(token.line, token.column),
                )
            case ">":
                return N.Gt(
                    token.value,
                    Pos(token.line, token.column),
                )
            case ">=":
                return N.GtE(
                    token.value,
                    Pos(token.line, token.column),
                )

    # ----------------------------- L_Assign_Alloc ----------------------------
    def prim_dt(self, token_list):
        token = token_list[0]
        match token.value:
            case "int":
                return N.IntType(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "char":
                return N.CharType(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "void":
                return N.VoidType(
                    token.value,
                    Pos(token.line, token.column),
                )

    # --------------------------------- L_Pntr --------------------------------
    def deref_offset_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "+":
                return N.Add(
                    token.value,
                    Pos(token.line, token.column),
                )
            case "-":
                return N.Sub(
                    token.value,
                    Pos(token.line, token.column),
                )

    # =========================================================================
    # =                                 Parser                                =
    # =========================================================================
    # --------------------------------- L_Arith -------------------------------
    def input_odp(self, _):
        return N.Call(N.Name("input"), [])

    def arith_opd(self, nodes):
        return nodes[0]

    def un_opd(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        match nodes[-2]:
            case N.LogicNot():
                acc_node = self._insert_to_bool(nodes[-1])
            case _:
                acc_node = nodes[-1]
        for node in nodes[-2::-1]:
            acc_node = N.UnOp(node, acc_node)
        return acc_node
        #  if len(nodes) == 1:
        #      return nodes[0]
        #  return N.UnOp(nodes[0], nodes[1])

    def arith_prec1(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = N.BinOp(acc_node, node1, node2)
        return acc_node

    def arith_prec2(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = N.BinOp(acc_node, node1, node2)
        return acc_node

    def arith_exp(self, nodes):
        return nodes[0]

    def print_stmt(self, nodes):
        return N.Exp(N.Call(N.Name("print"), [nodes[0]]))

    # --------------------------------- L_Logic -------------------------------
    def logic_atom(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return N.Atom(nodes[0], nodes[1], nodes[2])

    def _insert_to_bool(self, node):
        match node:
            # exclude all possible logic nodes
            case N.BinOp(_, N.LogicAnd(), _):
                return node
            case N.BinOp(_, N.LogicOr(), _):
                return node
            case N.Atom():
                return node
            case N.UnOp(N.LogicNot(), _):
                return node
            case N.BinOp():
                return N.ToBool(node)
            case N.UnOp():
                return N.ToBool(node)
            case N.Num():
                return N.ToBool(node)
            case N.Name():
                return N.ToBool(node)
            case N.Char():
                return N.ToBool(node)
            case _:
                bug_in_compiler(node)

    def logic_and(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        acc_node = self._insert_to_bool(nodes[0])
        for node in nodes[1:]:
            acc_node = N.BinOp(acc_node, N.LogicAnd(), self._insert_to_bool(node))
        return acc_node

    def logic_or(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        acc_node = self._insert_to_bool(nodes[0])
        for node in nodes[1:]:
            acc_node = N.BinOp(acc_node, N.LogicOr(), self._insert_to_bool(node))
        return acc_node

    def logic_exp(self, nodes):
        return nodes[0]

    # ----------------------------- L_Assign_Alloc ----------------------------
    def size_qual(self, nodes):
        return nodes[0]

    def alloc(self, nodes):
        return N.Alloc(N.Writeable(), nodes[0], nodes[1])

    def alloc_stmt(self, nodes):
        return N.Exp(nodes[0])

    def assign_stmt(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def init(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def const_init(self, nodes):
        return N.Assign(
            N.Alloc(N.Const(), nodes[0], nodes[1]),
            nodes[2],
        )

    def alloc_init_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Pntr --------------------------------
    def pntr_deg(self, nodes):
        return N.Num(str(len(nodes)))

    def pntr_decl(self, nodes):
        match nodes[0]:
            case N.Num("0"):
                return nodes[1]
            case _:
                return N.PntrDecl(nodes[0], nodes[1])

    def deref_loc(self, nodes):
        return nodes[0]

    def deref_simple(self, nodes):
        return N.Deref(nodes[0], N.Num("0"))

    def deref_arith(self, nodes):
        match nodes[1]:
            case N.Add():
                return N.Deref(nodes[0], nodes[2])
            case N.Sub():
                return N.Deref(nodes[0], N.UnOp(N.Minus(), nodes[2]))

    def deref(self, nodes):
        return nodes[0]

    def ref_loc(self, nodes):
        return nodes[0]

    def ref(self, nodes):
        return N.Ref(nodes[0])

    def pntr_opd(self, nodes):
        return nodes[0]

    # --------------------------------- L_Array -------------------------------
    def array_dims(self, nodes):
        return nodes

    def array_decl(self, nodes):
        match nodes[0]:
            case []:
                return nodes[1]
            case _:
                return N.ArrayDecl(nodes[0], nodes[1])

    def subscr_loc(self, nodes):
        return nodes[0]

    def array_subscr(self, nodes):
        return N.Subscr(nodes[0], nodes[1])

    def entry_subexp(self, nodes):
        return nodes[0]

    def array_subexps(self, nodes):
        return N.Array(nodes)

    def array_init_dims(self, nodes):
        return nodes

    def array_init_decl(self, nodes):
        return N.ArrayDecl(nodes[0], nodes[1])

    def array_init(self, nodes):
        return N.Assign(
            N.Alloc(
                N.Writeable(),
                nodes[0],
                nodes[1],
            ),
            nodes[2],
        )

    # -------------------------------- L_Struct -------------------------------
    def struct_spec(self, nodes):
        return N.StructSpec(nodes[0])

    def struct_attr(self, nodes):
        return N.Attr(nodes[0], nodes[1])

    def struct_params(self, nodes):
        params = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            params += [N.Param(node1, node2)]
        return params

    def struct_decl(self, nodes):
        return N.StructDecl(nodes[0], nodes[1])

    def struct_subexps(self, nodes):
        assigns = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            assigns += [N.Assign(node1, node2)]
        return N.Struct(assigns)

    def struct_init(self, nodes):
        return N.Assign(
            N.Alloc(
                N.Writeable(),
                nodes[0],
                N.PntrDecl(N.Num("0"), N.ArrayDecl(nodes[1], [])),
            ),
            nodes[2],
        )

    # -------------------------------- L_If_Else ------------------------------
    def if_stmt(self, nodes):
        return N.If(nodes[0], nodes[1])

    def if_else_stmt(self, nodes):
        if not isinstance(nodes[2], list):
            return N.IfElse(nodes[0], nodes[1], [nodes[2]])
        return N.IfElse(nodes[0], nodes[1], nodes[2])

    def if_if_else_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Loop --------------------------------
    def while_stmt(self, nodes):
        return N.While(nodes[0], nodes[1])

    def do_while_stmt(self, nodes):
        return N.DoWhile(nodes[1], nodes[0])

    def loop_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Stmt --------------------------------
    def decl_part(self, nodes):
        return nodes[0]

    def exec_part(self, nodes):
        return nodes[0]

    def exec_stmts(self, nodes):
        return nodes

    def decl_exec_stmts(self, nodes):
        return nodes

    # ---------------------------------- L_Fun --------------------------------
    def fun_call_args(self, nodes):
        return nodes

    def fun_call(self, nodes):
        return N.Call(nodes[0], nodes[1])

    def fun_call_stmt(self, nodes):
        return N.Exp(nodes[0])

    def fun_return(self, nodes):
        if len(nodes) == 0:
            return N.Return(N.Null())
        return N.Return(nodes[0])

    def fun_stmt(self, nodes):
        return nodes[0]

    def fun_params(self, nodes):
        params = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            params += [N.Param(node1, node2)]
        return params

    def fun_decl(self, nodes):
        return N.FunDecl(nodes[0], nodes[1], nodes[2])

    def fun_def(self, nodes):
        return N.FunDef(nodes[0], nodes[1], nodes[2], nodes[3])

    # --------------------------------- L_File --------------------------------
    def decl_def(self, nodes):
        return nodes[0]

    def decls_defs(self, nodes):
        return nodes

    def file(self, nodes):
        nodes[0].val = global_vars.path + nodes[0].val + ".ast"
        return N.File(nodes[0], nodes[1])

    # -------------------------------- L_Blocks -------------------------------
    def block(self, nodes):
        return N.Block(nodes[0], nodes[1])

    def blocks(self, nodes):
        return nodes

    def goto(self, nodes):
        return N.GoTo(nodes[0])
