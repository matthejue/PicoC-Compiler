from lark.visitors import Transformer
from lark.lexer import Token
import picoc_nodes as pn
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
        return pn.Name(token.value, Pos(token.line - 1, token.column - 1))

    def NUM(self, token: Token):
        return pn.Num(token.value, Pos(token.line - 1, token.column - 1))

    def CHAR(self, token: Token):
        return pn.Char(token.value[1:-1], Pos(token.line - 1, token.column - 1))

    def un_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "-":
                return pn.Minus(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "~":
                return pn.Not(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "!":
                return pn.LogicNot(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    def prec1_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "*":
                return pn.Mul(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "/":
                return pn.Div(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "%":
                return pn.Mod(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    def prec2_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "+":
                return pn.Add(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "-":
                return pn.Sub(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "^":
                return pn.Oplus(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "&":
                return pn.And(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "|":
                return pn.Or(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    # --------------------------------- L_Logic -------------------------------
    def relation(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "==":
                return pn.Eq(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "!=":
                return pn.NEq(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "<":
                return pn.Lt(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "<=":
                return pn.LtE(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case ">":
                return pn.Gt(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case ">=":
                return pn.GtE(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    # ----------------------------- L_Assign_Alloc ----------------------------
    def prim_dt(self, token_list):
        token = token_list[0]
        match token.value:
            case "int":
                return pn.IntType(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "char":
                return pn.CharType(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "void":
                return pn.VoidType(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    # --------------------------------- L_Pntr --------------------------------
    def deref_offset_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "+":
                return pn.Add(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "-":
                return pn.Sub(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )

    # =========================================================================
    # =                                 Parser                                =
    # =========================================================================
    # --------------------------------- L_Arith -------------------------------
    def input_odp(self, _):
        return pn.Call(pn.Name("input"), [])

    def arith_opd(self, nodes):
        return nodes[0]

    def un_opd(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        match nodes[-2]:
            case pn.LogicNot():
                acc_node = self._insert_to_bool(nodes[-1])
            case _:
                acc_node = nodes[-1]
        for node in nodes[-2::-1]:
            acc_node = pn.UnOp(node, acc_node)
        return acc_node
        #  if len(nodes) == 1:
        #      return nodes[0]
        #  return pn.UnOp(nodes[0], nodes[1])

    def arith_prec1(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = pn.BinOp(acc_node, node1, node2)
        return acc_node

    def arith_prec2(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = pn.BinOp(acc_node, node1, node2)
        return acc_node

    def arith_exp(self, nodes):
        return nodes[0]

    def print_stmt(self, nodes):
        return pn.Exp(pn.Call(pn.Name("print"), [nodes[0]]))

    # --------------------------------- L_Logic -------------------------------
    def logic_atom(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.Atom(nodes[0], nodes[1], nodes[2])

    def _insert_to_bool(self, node):
        match node:
            # exclude all possible logic nodes
            case pn.BinOp(_, pn.LogicAnd(), _):
                return node
            case pn.BinOp(_, pn.LogicOr(), _):
                return node
            case pn.Atom():
                return node
            case pn.UnOp(pn.LogicNot(), _):
                return node
            case pn.BinOp():
                return pn.ToBool(node)
            case pn.UnOp():
                return pn.ToBool(node)
            case pn.Num():
                return pn.ToBool(node)
            case pn.Name():
                return pn.ToBool(node)
            case pn.Char():
                return pn.ToBool(node)
            case _:
                bug_in_compiler(node)

    def logic_and(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        acc_node = self._insert_to_bool(nodes[0])
        for node in nodes[1:]:
            acc_node = pn.BinOp(acc_node, pn.LogicAnd(), self._insert_to_bool(node))
        return acc_node

    def logic_or(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        acc_node = self._insert_to_bool(nodes[0])
        for node in nodes[1:]:
            acc_node = pn.BinOp(acc_node, pn.LogicOr(), self._insert_to_bool(node))
        return acc_node

    def logic_exp(self, nodes):
        return nodes[0]

    # ----------------------------- L_Assign_Alloc ----------------------------
    def size_qual(self, nodes):
        return nodes[0]

    def alloc(self, nodes):
        return pn.Alloc(pn.Writeable(), nodes[0], nodes[1])

    def alloc_stmt(self, nodes):
        return pn.Exp(nodes[0])

    def assign_stmt(self, nodes):
        return pn.Assign(nodes[0], nodes[1])

    def init(self, nodes):
        return pn.Assign(nodes[0], nodes[1])

    def const_init(self, nodes):
        return pn.Assign(
            pn.Alloc(pn.Const(), nodes[0], nodes[1]),
            nodes[2],
        )

    def alloc_init_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Pntr --------------------------------
    def pntr_deg(self, nodes):
        return pn.Num(str(len(nodes)))

    def pntr_decl(self, nodes):
        match nodes[0]:
            case pn.Num("0"):
                return nodes[1]
            case _:
                return pn.PntrDecl(nodes[0], nodes[1])

    def deref_loc(self, nodes):
        return nodes[0]

    def deref_simple(self, nodes):
        return pn.Deref(nodes[0], pn.Num("0"))

    def deref_arith(self, nodes):
        match nodes[1]:
            case pn.Add():
                return pn.Deref(nodes[0], nodes[2])
            case pn.Sub():
                return pn.Deref(nodes[0], pn.UnOp(pn.Minus(), nodes[2]))

    def deref(self, nodes):
        return nodes[0]

    def ref_loc(self, nodes):
        return nodes[0]

    def ref(self, nodes):
        return pn.Ref(nodes[0])

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
                return pn.ArrayDecl(nodes[0], nodes[1])

    def subscr_loc(self, nodes):
        return nodes[0]

    def array_subscr(self, nodes):
        return pn.Subscr(nodes[0], nodes[1])

    def entry_subexp(self, nodes):
        return nodes[0]

    def array_subexps(self, nodes):
        return pn.Array(nodes)

    def array_init_dims(self, nodes):
        return nodes

    def array_init_decl(self, nodes):
        return pn.ArrayDecl(nodes[0], nodes[1])

    def array_init(self, nodes):
        return pn.Assign(
            pn.Alloc(
                pn.Writeable(),
                nodes[0],
                nodes[1],
            ),
            nodes[2],
        )

    # -------------------------------- L_Struct -------------------------------
    def struct_spec(self, nodes):
        return pn.StructSpec(nodes[0])

    def struct_attr(self, nodes):
        return pn.Attr(nodes[0], nodes[1])

    def struct_params(self, nodes):
        params = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            params += [pn.Param(node1, node2)]
        return params

    def struct_decl(self, nodes):
        return pn.StructDecl(nodes[0], nodes[1])

    def struct_subexps(self, nodes):
        assigns = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            assigns += [pn.Assign(node1, node2)]
        return pn.Struct(assigns)

    def struct_init(self, nodes):
        return pn.Assign(
            pn.Alloc(
                pn.Writeable(),
                nodes[0],
                pn.PntrDecl(pn.Num("0"), pn.ArrayDecl(nodes[1], [])),
            ),
            nodes[2],
        )

    # -------------------------------- L_If_Else ------------------------------
    def if_stmt(self, nodes):
        return pn.If(nodes[0], nodes[1])

    def if_else_stmt(self, nodes):
        if not isinstance(nodes[2], list):
            return pn.IfElse(nodes[0], nodes[1], [nodes[2]])
        return pn.IfElse(nodes[0], nodes[1], nodes[2])

    def if_if_else_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Loop --------------------------------
    def while_stmt(self, nodes):
        return pn.While(nodes[0], nodes[1])

    def do_while_stmt(self, nodes):
        return pn.DoWhile(nodes[1], nodes[0])

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
        return pn.Call(nodes[0], nodes[1])

    def fun_call_stmt(self, nodes):
        return pn.Exp(nodes[0])

    def fun_return(self, nodes):
        if len(nodes) == 0:
            return pn.Return(pn.Null())
        return pn.Return(nodes[0])

    def fun_stmt(self, nodes):
        return nodes[0]

    def fun_params(self, nodes):
        params = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            params += [pn.Param(node1, node2)]
        return params

    def fun_decl(self, nodes):
        return pn.FunDecl(nodes[0], nodes[1], nodes[2])

    def fun_def(self, nodes):
        return pn.FunDef(nodes[0], nodes[1], nodes[2], nodes[3])

    # --------------------------------- L_File --------------------------------
    def decl_def(self, nodes):
        return nodes[0]

    def decls_defs(self, nodes):
        return nodes

    def file(self, nodes):
        nodes[0].val = global_vars.path + nodes[0].val + ".ast"
        return pn.File(nodes[0], nodes[1])

    # -------------------------------- L_Blocks -------------------------------
    def block(self, nodes):
        return pn.Block(nodes[0], nodes[1])

    def blocks(self, nodes):
        return nodes

    def goto(self, nodes):
        return pn.GoTo(nodes[0])
