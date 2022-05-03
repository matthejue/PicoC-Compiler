#!/usr/bin/python

from lark import Lark, Transformer, Token
from picoc_nodes import N
from errors import Errors


def replace_token(token: Token):
    if token.type == "NAME":
        return N.Name(token.value, (token.start_pos, token.end_pos))
    elif token.type == "NUM":
        return N.Num(token.value, (token.start_pos, token.end_pos))
    elif token.type == "CHAR":
        return N.Char(token.value, (token.start_pos, token.end_pos))


class ASTTransformer(Transformer):
    # -------------------------------------------------------------------------
    # -                                 Lexer                                 -
    # -------------------------------------------------------------------------
    # --------------------------------- L_Arith -------------------------------
    def NAME(self, token):
        return N.Name(token.vaue, (token.start_pos, token.end_pos))

    def NUM(self, token):
        return N.Num(token.value, (token.start_pos, token.end_pos))

    def CHAR(self, token):
        return N.Char(token.value, (token.start_pos, token.end_pos))

    def UN_OP(self, token):
        match token.value:
            case "-":
                return N.Minus(token.value, (token.start_pos, token.end_pos))
            case "~":
                return N.Not(token.value, (token.start_pos, token.end_pos))
            case "!":
                return N.LogicNot(token.value, (token.start_pos, token.end_pos))

    def PREC1_OP(self, token):
        match token.value:
            case "*":
                return N.Add(token.value, (token.start_pos, token.end_pos))
            case "/":
                return N.Div(token.value, (token.start_pos, token.end_pos))
            case "%":
                return N.Mod(token.value, (token.start_pos, token.end_pos))

    def PREC2_OP(self, token):
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
    def RELATION(self, token):
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
    def PRIM_SIZE_QUAL(self, token):
        match token.value:
            case "int":
                return N.IntType(token.value, (token.start_pos, token.end_pos))
            case "char":
                return N.CharType(token.value, (token.start_pos, token.end_pos))
            case "void":
                return N.VoidType(token.value, (token.start_pos, token.end_pos))

    # -------------------------------------------------------------------------
    # -                                 Parser                                -
    # -------------------------------------------------------------------------
    # --------------------------------- L_Arith -------------------------------
    def input_odp(self, _):
        return N.Call("input", [])

    def arith_opd(self, nodes):
        return nodes[0]

    def un_opd(self, nodes):
        if len(nodes) == 2:
            return N.UnOp(nodes[0], nodes[1])
        if len(nodes) == 1:
            return nodes[0]

    def arith_prec1(self, nodes):
        return N.BinOp(nodes[0], nodes[1], nodes[2])

    def arith_prec2(self, nodes):
        return N.BinOp(nodes[0], nodes[1], nodes[2])

    def arith_exp(self, nodes):
        return nodes[0]

    def print_stmt(self, nodes):
        return N.Call("print", nodes)

    # --------------------------------- L_Logic -------------------------------
    def to_bool(self, nodes):
        return N.ToBool(nodes[0])

    def logic_opd(self, nodes):
        return nodes[0]

    def logic_atom(self, nodes):
        return N.Atom(nodes[0], nodes[1], nodes[2])

    def logic_and(self, nodes):
        return N.BinOp(nodes[0], nodes[1], nodes[2])

    def logic_or(self, nodes):
        return N.BinOp(nodes[0], nodes[1], nodes[2])

    def logic_exp(self, nodes):
        return nodes[0]

    def arith_exp_logic_exp(self, nodes):
        return nodes[0]

    # ----------------------------- L_Assign_Alloc ----------------------------
    def size_qual(self, nodes):
        return nodes[0]

    def alloc(self, nodes):
        return N.Alloc(N.Writeable(), nodes[0], nodes[1])

    def var_assign(self, nodes):
        return N.Assign(nodes[0], nodes[1])

    def assign(self, nodes):
        return nodes[0]

    def init(self, nodes):
        return N.Assign(N.Alloc(N.Writeable(), nodes[0], nodes[1]), nodes[2])

    def const_init(self, nodes):
        return N.Assign(N.Alloc(N.Const(), nodes[0], nodes[1]), nodes[2])

    def assign_alloc_stmt(self, nodes):
        return nodes[0]

    # -------------------------------- L_Pointer ------------------------------
    def pntr_size_qual(self, nodes):
        return N.PointerType(nodes[0])

    def pntr_simple(self, nodes):
        return N.Deref(nodes[0], 0)

    def pntr_arith(self, nodes_token):
        match nodes_token[1].value:
            case "+":
                return N.Deref(nodes_token[0], nodes_token[2])
            case "-":
                return N.Deref(nodes_token[0], N.UnOp(N.Minus(), nodes_token[2]))

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
    def array_size_qual(self, nodes):
        return N.ArrayType(nodes[0])

    def array_init(self, nodes):
        return N.Assign(N.Alloc(N.Writeable(), nodes[]), N.Array(None, nodes))

    def subscript(self, nodes):
        return N.Subscript(nodes[0], nodes[1])

    def array_opd(self, nodes):
        return nodes[0]

    def array_ref(self, nodes):
        return N.Ref(nodes)

    def array_assign(self, nodes):
        return N.Assign(nodes)

    # -------------------------------- L_Struct -------------------------------
    def struct_size_qual(self, nodes):
        return N.StructType(nodes)

    def struct_creation(self, nodes):
        return N.Struct(nodes)

    def attr(self, nodes):
        return N.Attribute(nodes)

    def struct_opd(self, nodes):
        return nodes[0]

    def struct_ref(self, nodes):
        return N.Ref(nodes)

    def struct_assign(self, nodes):
        return N.Assign(nodes)

    def struct_decl_stmt(self, nodes):
        return N.StructDecl(nodes)

    # -------------------------------- L_If_Else ------------------------------
    def if_(self, nodes):
        return N.If(nodes)

    def if_else(self, nodes):
        for (i, child) in enumerate(nodes):
            match child:
                case N.Else():
                    break
        else:
            # should never happen
            ...
        return N.IfElse(nodes[0], nodes[1:i], nodes[i + 1 :])

    def if_else_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Loop --------------------------------
    def while_(self, nodes):
        return N.While(nodes)

    def do_while(self, nodes):
        return N.DoWhile(nodes)

    def loop_stmt(self, nodes):
        return nodes[0]

    # --------------------------------- L_Stmt --------------------------------
    def stmt(self, nodes):
        return nodes[0]

    # ---------------------------------- L_Fun --------------------------------
    def fun_size_qual(self, nodes):
        return N.FunType(nodes)

    def fun_call(self, nodes):
        return N.Call(nodes)

    def fun_opd(self, nodes):
        return nodes[0]

    def return_(self, nodes):
        return N.Return(nodes)

    def fun_stmt(self, nodes):
        return nodes[0]

    def def_(self, nodes):
        for (i, child) in enumerate(nodes[2:]):
            match child:
                case N.Param(_, _):
                    pass
                case _:
                    break
        else:
            # TODO: error message
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
