#!/usr/bin/python

from lark import Lark, Transformer, Token
from picoc_nodes import N
from errors import Errors


def replace_token(token: Token):
    if token.type == "NAME":
        return N.Name(token.value, (token.start_pos, token.end_pos))
    elif token.type == "":
        ...


class ASTTransformer(Transformer):
    # --------------------------------- L_Arith -------------------------------
    def input_odp(self, nodes):
        return N.Call("input", nodes)

    def arith_opd(self, nodes):
        return nodes

    def un_opd(self, nodes):
        return N.UnOp(nodes)

    def arith_prec1(self, nodes):
        return N.BinOp(nodes)

    def arith_prec2(self, nodes):
        return N.BinOp(nodes)

    def arith_exp(self, nodes):
        return nodes

    def print_stmt(self, nodes):
        return N.Call("print", nodes)

    # --------------------------------- L_Logic -------------------------------
    def to_bool(self, nodes):
        return N.ToBool(nodes)

    def logic_opd(self, nodes):
        return nodes

    def logic_not(self, nodes):
        return N.UnOp(nodes)

    def logic_atom(self, nodes):
        return N.Atom(nodes)

    def logic_and(self, nodes):
        return N.BinOp(nodes)

    def logic_or(self, nodes):
        return N.BinOp(nodes)

    def logic_exp(self, nodes):
        return nodes

    # ----------------------------- L_Assign_Alloc ----------------------------
    def size_qual(self, nodes):
        return nodes

    def alloc(self, nodes):
        return N.Alloc(nodes)

    def var_assign(self, nodes):
        return N.Assign(nodes)

    def assign(self, nodes):
        return nodes

    def init(self, nodes):
        return N.Assign(nodes)

    def const_init(self, nodes):
        return N.Assign(nodes)

    def assign_alloc_stmt(self, nodes):
        return N.Assign(nodes)

    # -------------------------------- L_Pointer ------------------------------
    def pntr_size_qual(self, nodes):
        return N.PointerType(nodes)

    def pntr_simple(self, nodes):
        return N.Deref(nodes)

    def pntr_arith(self, nodes):
        return N.Deref(nodes)

    def deref(self, nodes):
        return nodes

    def var_ref(self, nodes):
        return N.Ref(nodes)

    def pntr_ref(self, nodes):
        return N.Ref(nodes)

    def ref(self, nodes):
        return nodes

    def pntr_opd(self, nodes):
        return nodes

    def pntr_assign(self, nodes):
        return N.Assign(nodes)

    # --------------------------------- L_Array -------------------------------
    def array_size_qual(self, nodes):
        return N.ArrayType(nodes)

    def array_creation(self, nodes):
        return N.Array(nodes)

    def subscript(self, nodes):
        return N.Attribute(nodes)

    def array_opd(self, nodes):
        return nodes

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
        return nodes

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
        return nodes

    # --------------------------------- L_Loop --------------------------------
    def while_(self, nodes):
        return N.While(nodes)

    def do_while(self, nodes):
        return N.DoWhile(nodes)

    def loop_stmt(self, nodes):
        return nodes

    # --------------------------------- L_Stmt --------------------------------
    def stmt(self, nodes):
        return nodes

    # ---------------------------------- L_Fun --------------------------------
    def fun_size_qual(self, nodes):
        return N.FunType(nodes)

    def fun_call(self, nodes):
        return N.Call(nodes)

    def fun_opd(self, nodes):
        return nodes

    def return_(self, nodes):
        return N.Return(nodes)

    def fun_stmt(self, nodes):
        return nodes

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
