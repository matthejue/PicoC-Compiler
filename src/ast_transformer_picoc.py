from lark.visitors import Transformer
from lark.lexer import Token
import picoc_nodes as pn
from global_classes import Pos
from global_funs import bug_in_compiler, remove_extension, nodes_to_str
import errors


class ASTTransformerPicoC(Transformer):
    # =========================================================================
    # =                                 Lexer                                 =
    # =========================================================================
    # --------------------------------- L_Arith -------------------------------
    def NUM(self, token: Token):
        return pn.Num(token.value, Pos(token.line - 1, token.column - 1))

    def CHAR(self, token: Token):
        return pn.Char(token.value[1:-1], Pos(token.line - 1, token.column - 1))

    def FILENAME(self, token: Token):
        return pn.Name(token.value, Pos(token.line - 1, token.column - 1))

    def name(self, token_list):
        token = token_list[0]
        return pn.Name(token.value, Pos(token.line - 1, token.column - 1))

    def un_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
            case "-":
                return pn.Minus(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "!":
                return pn.LogicNot(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "~":
                return pn.Not(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "*":
                return pn.DerefOp(
                    token.value,
                    Pos(token.line - 1, token.column - 1),
                )
            case "&":
                return pn.RefOp(
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

    # --------------------------------- L_Logic -------------------------------
    def rel_op(self, token_list: list[Token]):
        token = token_list[0]
        match token.value:
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

    def eq_op(self, token_list: list[Token]):
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

    # =========================================================================
    # =                                 Parser                                =
    # =========================================================================
    # ------------- L_Arith + L_Array + L_Pntr + L_Struct + L_Fun -------------
    def prim_exp(self, nodes):
        return nodes[0]

    def post_exp(self, nodes):
        return nodes[0]

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
                bug_in_compiler(current_bin_exp)

    def un_exp(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        un_op = nodes[0]
        exp = nodes[1]
        match un_op:
            case (pn.Minus() | pn.Not()):
                return pn.UnOp(un_op, exp)
            case pn.LogicNot():
                return pn.UnOp(un_op, self._insert_to_bool(exp))
            case pn.DerefOp():
                exp1, bin_op, exp2 = self._leftmost_node(exp)
                match bin_op:
                    case pn.Add():
                        return pn.Deref(exp1, exp2)
                    case pn.Sub():
                        return pn.Deref(exp1, pn.UnOp(pn.Minus(), exp2))
                    case None:
                        return pn.Deref(exp1, pn.Num("0"))
                    case _:
                        raise errors.UnexpectedToken(
                            nodes_to_str([pn.Add, pn.Sub]), bin_op.val, bin_op.pos
                        )
            case pn.RefOp():
                return pn.Ref(exp)
            case _:
                bug_in_compiler(nodes)

    # --------------------------------- L_Arith -------------------------------
    def input_exp(self, _):
        return pn.Call(pn.Name("input"), [])

    def print_exp(self, nodes):
        return pn.Call(pn.Name("print"), [nodes[0]])

    def arith_prec1(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(nodes[0], nodes[1], nodes[2])

    def arith_prec2(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(nodes[0], nodes[1], nodes[2])

    def arith_and(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(nodes[0], pn.And(), nodes[1])

    def arith_oplus(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(nodes[0], pn.Oplus(), nodes[1])

    def arith_or(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(nodes[0], pn.Or(), nodes[1])

    # --------------------------------- L_Logic -------------------------------
    def rel_exp(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.Atom(nodes[0], nodes[1], nodes[2])

    def eq_exp(self, nodes):
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
        return pn.BinOp(
            self._insert_to_bool(nodes[0]),
            pn.LogicAnd(),
            self._insert_to_bool(nodes[1]),
        )

    def logic_or(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return pn.BinOp(
            self._insert_to_bool(nodes[0]),
            pn.LogicOr(),
            self._insert_to_bool(nodes[1]),
        )

    # ----------------------------- L_Assign_Alloc ----------------------------
    def type_spec(self, nodes):
        return nodes[0]

    def alloc(self, nodes):
        return pn.Alloc(pn.Writeable(), nodes[0], nodes[1])

    def assign_stmt(self, nodes):
        return pn.Assign(nodes[0], nodes[1])

    def bug_initializer(self, nodes):
        return nodes[0]

    def init_stmt(self, nodes):
        return pn.Assign(nodes[0], nodes[1])

    def const_init_stmt(self, nodes):
        return pn.Assign(
            pn.Alloc(pn.Const(), nodes[0], nodes[1]),
            nodes[2],
        )

    # --------------------------------- L_Array -------------------------------
    def array_dims(self, nodes):
        return nodes

    def array_decl(self, nodes):
        match nodes[0]:
            case []:
                return nodes[1]
            case _:
                return pn.ArrayDecl(nodes[0], nodes[1])

    def array_init(self, nodes):
        return pn.Array(nodes)

    def array_subscr(self, nodes):
        # TODO: Fehlermeldungen, wenn da eine Num ist
        return pn.Subscr(nodes[0], nodes[1])

    # --------------------------------- L_Pntr --------------------------------
    def pntr_deg(self, nodes):
        return pn.Num(str(len(nodes)))

    def pntr_decl(self, nodes):
        match nodes[0]:
            case pn.Num("0"):
                return nodes[1]
            case _:
                return pn.PntrDecl(nodes[0], nodes[1])

    # -------------------------------- L_Struct -------------------------------
    def struct_spec(self, nodes):
        return pn.StructSpec(nodes[0])

    def struct_params(self, nodes):
        return nodes

    def struct_decl(self, nodes):
        return pn.StructDecl(nodes[0], nodes[1])

    def struct_init(self, nodes):
        assigns = []
        for node1, node2 in zip(nodes[0::2], nodes[1::2]):
            assigns += [pn.Assign(node1, node2)]
        return pn.Struct(assigns)

    def struct_attr(self, nodes):
        return pn.Attr(nodes[0], nodes[1])

    # -------------------------------- L_If_Else ------------------------------
    def if_stmt(self, nodes):
        node1 = nodes[1] if isinstance(nodes[1], list) else [nodes[1]]
        return pn.If(nodes[0], node1)

    def if_else_stmt(self, nodes):
        node1 = nodes[1] if isinstance(nodes[1], list) else [nodes[1]]
        node2 = nodes[2] if isinstance(nodes[2], list) else [nodes[2]]
        return pn.IfElse(nodes[0], node1, node2)

    # --------------------------------- L_Loop --------------------------------
    def while_stmt(self, nodes):
        node1 = nodes[1] if isinstance(nodes[1], list) else [nodes[1]]
        return pn.While(nodes[0], node1)

    def do_while_stmt(self, nodes):
        node0 = nodes[0] if isinstance(nodes[0], list) else [nodes[0]]
        return pn.DoWhile(nodes[1], node0)

    # --------------------------------- L_Stmt --------------------------------
    def decl_exp_stmt(self, nodes):
        return pn.Exp(nodes[0])

    def decl_direct_stmt(self, nodes):
        return nodes[0]

    def decl_part(self, nodes):
        return nodes[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compound_stmt(self, nodes):
        return nodes

    def exec_exp_stmt(self, nodes):
        return pn.Exp(nodes[0])

    def exec_direct_stmt(self, nodes):
        return nodes[0]

    def exec_part(self, nodes):
        return nodes[0]

    def decl_exec_stmts(self, nodes):
        return nodes

    # ---------------------------------- L_Fun --------------------------------
    def fun_args(self, nodes):
        return nodes

    def fun_call(self, nodes):
        return pn.Call(nodes[0], nodes[1])

    def fun_return_stmt(self, nodes):
        if len(nodes) == 0:
            return pn.Return()
        return pn.Return(nodes[0])

    def fun_params(self, nodes):
        return nodes

    def fun_decl(self, nodes):
        match nodes[1]:
            case pn.Num("0"):
                return pn.FunDecl(nodes[0], nodes[2], nodes[3])
            case _:
                return pn.FunDecl(pn.PntrDecl(nodes[1], nodes[0]), nodes[2], nodes[3])

    def fun_def(self, nodes):
        match nodes[1]:
            case pn.Num("0"):
                return pn.FunDef(nodes[0], nodes[2], nodes[3], nodes[4])
            case _:
                return pn.FunDef(
                    pn.PntrDecl(nodes[1], nodes[0]), nodes[2], nodes[3], nodes[4]
                )

    # --------------------------------- L_File --------------------------------
    def decl_def(self, nodes):
        return nodes[0]

    def decls_defs(self, nodes):
        return nodes

    def file(self, nodes):
        nodes[0].val = remove_extension(nodes[0].val) + ".ast"
        return pn.File(nodes[0], nodes[1])
