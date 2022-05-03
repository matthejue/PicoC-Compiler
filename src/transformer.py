#!/usr/bin/python

from lark import Lark, Transformer, Token
from picoc_nodes import N
from errors import Errors


class ASTTransformer(Transformer):
    # -------------------------------------------------------------------------
    # -                                 Lexer                                 -
    # -------------------------------------------------------------------------
    # --------------------------------- L_Arith -------------------------------
    def NAME(self, token: Token):
        return N.Name(token.value, (token.start_pos, token.end_pos))

    def NUM(self, token: Token):
        return N.Num(token.value, (token.start_pos, token.end_pos))

    def CHAR(self, token: Token):
        return N.Char(token.value, (token.start_pos, token.end_pos))

    def UN_OP(self, token: Token):
        match token.value:
            case "-":
                return N.Minus(token.value, (token.start_pos, token.end_pos))
            case "~":
                return N.Not(token.value, (token.start_pos, token.end_pos))
            case "!":
                return N.LogicNot(token.value, (token.start_pos, token.end_pos))

    def PREC1_OP(self, token: Token):
        match token.value:
            case "*":
                return N.Add(token.value, (token.start_pos, token.end_pos))
            case "/":
                return N.Div(token.value, (token.start_pos, token.end_pos))
            case "%":
                return N.Mod(token.value, (token.start_pos, token.end_pos))

    def PREC2_OP(self, token: Token):
        match token.value:
            case "+":
                return N.Add(token.value, (token.start_pos, token.end_pos))
            case "-":
                return N.Sub(token.value, (token.start_pos, token.end_pos))
            case "^":
                return N.Oplus(token.value, (token.start_pos, token.end_pos))
            case "&":
                return N.And(token.value, (token.start_pos, token.end_pos))
            case "|":
                return N.Or(token.value, (token.start_pos, token.end_pos))

    # --------------------------------- L_Logic -------------------------------
    def RELATION(self, token: Token):
        match token.value:
            case "==":
                return N.Eq(token.value, (token.start_pos, token.end_pos))
            case "!=":
                return N.NEq(token.value, (token.start_pos, token.end_pos))
            case "<":
                return N.Lt(token.value, (token.start_pos, token.end_pos))
            case "<=":
                return N.LtE(token.value, (token.start_pos, token.end_pos))
            case ">":
                return N.Gt(token.value, (token.start_pos, token.end_pos))
            case ">=":
                return N.GtE(token.value, (token.start_pos, token.end_pos))

    # ----------------------------- L_Assign_Alloc ----------------------------
    def PRIM_SIZE_QUAL(self, token: Token):
        match token.value:
            case "int":
                return N.IntType(token.value, (token.start_pos, token.end_pos))
            case "char":
                return N.CharType(token.value, (token.start_pos, token.end_pos))
            case "void":
                return N.VoidType(token.value, (token.start_pos, token.end_pos))

    # ------------------------------- L_Pointer -------------------------------
    def PNTR_PLUS(self, token: Token):
        return N.PNTR_PLUS(token.value, (token.start_pos, token.end_pos))

    def PNTR_MINUS(self, token: Token):
        return N.PNTR_MINUS(token.value, (token.start_pos, token.end_pos))

    # ------------------------------- L_If_Else -------------------------------
    def ELSE(self, token: Token):
        return N.Else(token.value, (token.start_pos, token.end_pos))

    # -------------------------------------------------------------------------
    # -                                 Parser                                -
    # -------------------------------------------------------------------------
    # --------------------------------- L_Arith -------------------------------
    def input_odp(self, _):
        return N.Call("input", [])

    def arith_opd(self, nodes):
        return nodes[0]

    def un_opd(self, nodes):
        acc_node = nodes[-1]
        for node in nodes[-2::-1]:
            acc_node = N.UnOp(node, acc_node)
        return acc_node

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
        return N.Call("print", nodes[0])

    # --------------------------------- L_Logic -------------------------------
    def to_bool(self, nodes):
        return N.ToBool(nodes[0])

    def logic_opd(self, nodes):
        return nodes[0]

    def logic_atom(self, nodes):
        if len(nodes) == 1:
            return nodes[0]
        return N.Atom(nodes[0], nodes[1], nodes[2])

    def logic_and(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = N.BinOp(acc_node, node1, node2)
        return acc_node

    def logic_or(self, nodes):
        acc_node = nodes[0]
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            acc_node = N.BinOp(acc_node, node1, node2)
        return acc_node

    def logic_exp(self, nodes):
        return nodes[0]

    def arith_exp_logic_exp(self, nodes):
        return nodes[0]

    # ----------------------------- L_Assign_Alloc ----------------------------
    def datatype(self, nodes):
        return nodes[0]

    def alloc(self, nodes):
        return N.Alloc(N.Writeable(), nodes[0], nodes[1], nodes[2], nodes[3])

    def alloc_stmt(self, nodes):
        return nodes[0]

    def var_assign(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def assign(self, nodes):
        return nodes[0]

    def init(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def const_init(self, nodes):
        return N.Assign(
            N.Alloc(
                N.Const(), nodes[0], N.PntrDecl(N.Num(0)), nodes[1], N.ArrayDecl([])
            ),
            nodes[2],
        )

    def assign_alloc_stmt(self, nodes):
        return nodes[0]

    # -------------------------------- L_Pointer ------------------------------
    def pntr_decl(self, nodes):
        return N.PntrDecl(N.Num(len(nodes)))

    def pntr_simple(self, nodes):
        return N.Deref(nodes[0], 0)

    def pntr_arith(self, nodes):
        match nodes[1]:
            case N.PNTR_PLUS():
                return N.Deref(nodes[0], nodes[2])
            case N.PNTR_MINUS():
                return N.Deref(nodes[0], N.UnOp(N.Minus(), nodes[2]))

    def deref(self, nodes):
        return nodes[0]

    def var_ref(self, nodes):
        return N.Ref(nodes[0])

    def pntr_ref(self, nodes):
        return N.Ref(nodes[0])

    def ref(self, nodes):
        return nodes[0]

    def pntr_opd(self, nodes):
        return nodes[0]

    def pntr_assign(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    # --------------------------------- L_Array -------------------------------
    def array_decl(self, nodes):
        return N.ArrayDecl(nodes)

    def array_subscr(self, nodes):
        return N.Subscript(nodes[0], nodes[1])

    def array_ref(self, nodes):
        return N.Ref(nodes[0])

    def array_assign(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def array_subexp(self, nodes):
        return N.Array(nodes)

    def entry_subexp(self, nodes):
        return nodes[0]

    def array_init(self, nodes):
        return N.Assign(
            N.Alloc(N.Writeable(), nodes[0], N.PntrDecl(N.Num(0)), nodes[1], nodes[2]),
            N.Array(nodes[3:]),
        )

    # -------------------------------- L_Struct -------------------------------
    def struct_spec(self, nodes):
        return N.StructSpec(nodes[0])

    def struct_attr(self, nodes):
        return N.Attr(nodes[0], nodes[1])

    def struct_ref(self, nodes):
        return N.Ref(nodes[0])

    def struct_assign(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def struct_decl_stmt(self, nodes):
        params = []
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            params += [N.Param(node1, node2)]
        return N.StructDecl(nodes[0], params)

    def struct_subexp(self, nodes):
        assigns = []
        for node1, node2 in zip(nodes[1::2], nodes[2::2]):
            assigns += [N.Assign(node1, node2)]
        return N.Struct(assigns)

    def struct_init(self, nodes):
        assigns = []
        for node1, node2 in zip(nodes[2::2], nodes[3::2]):
            assigns += [N.Assign(node1, node2)]
        return N.Assign(
            N.Alloc(
                N.Writeable(), nodes[0], N.PntrDecl(N.Num(0)), nodes[1], N.ArrayDecl([])
            ),
            N.Struct(assigns),
        )

    # -------------------------------- L_If_Else ------------------------------
    def if_(self, nodes):
        return N.If(nodes[0], nodes[1:])

    def if_else(self, nodes):
        for (i, node) in enumerate(nodes):
            match node:
                case N.Else():
                    break
        return N.IfElse(nodes[0], nodes[1:i], nodes[i + 1 :])

    def if_else_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Loop --------------------------------
    def while_(self, nodes):
        return N.While(nodes[0], nodes[1:])

    def do_while(self, nodes):
        return N.DoWhile(nodes[-1], nodes[0:-1])

    def loop_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Stmt --------------------------------
    def stmt(self, nodes):
        return nodes[0]

    # ---------------------------------- L_Fun --------------------------------
    def fun_call(self, nodes):
        return N.Call(nodes[0], nodes[1:])

    def fun_call_stmt(self, nodes):
        return N.Exp(nodes[0])

    def return_(self, nodes):
        return N.Return(nodes[0])

    def fun_stmt(self, nodes):
        return nodes[0]

    def def_(self, nodes):
        for (i, child) in enumerate(nodes[2:]):
            match child:
                case N.Name(_, _):
                    i -= 1
                    pass
                case _:
                    break
            ...
        return N.FunDef(nodes[0], nodes[1], nodes[2:i], nodes[i:])

    # --------------------------------- L_File --------------------------------
    def file(self, nodes):
        for (i, node) in enumerate(nodes):
            match node:
                case N.FunDef(N.Name("main"), _, _, _):
                    break
        else:
            raise Errors.NoMainFunctionError(str(nodes[0].value))
        return N.File(nodes[0], nodes[i], nodes[1:i] + nodes[i + 1 :])


#  ----------------------------------------------------------------------------
#  -                                  Testing                                 -
#  ----------------------------------------------------------------------------
with open("./concrete_syntax.lark") as fin:
    parser = Lark(fin.read(), start="file")
    dt = parser.parse(
        r"""
        testus
        char test(){
            int var = ----10;  // das ist doof
            char pntr = *(var + 10);
            var = 10 + 3;
        }
        """
        #  r"""
        #  test
        #  int test(char c, int var){
        #  print(_fun120 /*-3*/ + 120 * -'c');
        #  int[] var = {12, 3, 4}; // das ist blöd
        #  // das ist noch blöder
        #  var[3] = 10;
        #  }
        #  """
    )
    ast = ASTTransformer().transform(dt)
    print(dt.pretty())
    print(dt)
    print(ast)
