#!/usr/bin/python

from lark import Lark, Transformer, Token
from picoc_nodes import N


class ASTTransformer(Transformer):
    # ----------------------------- L_Assign_Alloc ----------------------------
    def input_odp(self):
        ...

    def arith_opd(self, nodes):
        print("arith_opd", nodes)
        return nodes

    def unary_opd(self, nodes):
        print("unary_opd", nodes)
        return nodes

    def arith_prec1(self, nodes):
        print("arith_prec1", nodes)
        return nodes

    def arith_prec2(self, nodes):
        print("arith_prec2", nodes)
        return nodes

    def arith_exp(self, nodes):
        print("arith_exp", nodes)
        return nodes

    def print_stmt(self):
        ...

    # --------------------------------- L_Logic -------------------------------
    def logic_opd(self, nodes):
        print("logic_opd", nodes)
        return nodes

    def logic_not(self, nodes):
        print("logic_not", nodes)
        return nodes

    def logic_atom(self, nodes):
        print("logic_atom", nodes)
        return nodes

    def logic_and(self, nodes):
        print("logic_and", nodes)
        return nodes

    def logic_or(self, nodes):
        print("logic_or", nodes)
        return nodes

    def logic_exp(self, nodes):
        print("logic_exp", nodes)
        return nodes

    # ----------------------------- L_Assign_Alloc ----------------------------
    def size_qual(self, nodes):
        print("size_qual", nodes)
        return nodes

    def alloc(self):
        ...

    def var_assign(self):
        ...

    def assign(self):
        ...

    def init(self, nodes):
        print("init", nodes)
        return nodes

    def const_init(self):
        ...

    def assign_alloc_stmt(self, nodes):
        print("assign_alloc_stmt", nodes)
        return nodes

    # -------------------------------- L_Pointer ------------------------------
    def pntr_size_qual(self, nodes):
        print("pntr_size_qual", nodes)
        return nodes

    def pntr_simple(self):
        ...

    def pntr_arith(self):
        ...

    def deref(self):
        ...

    def var_ref(self, nodes):
        print("var_ref", nodes)
        return nodes

    def pntr_ref(self):
        ...

    def ref(self, nodes):
        print("ref", nodes)
        return nodes

    def pntr_opd(self, nodes):
        print("pntr_opd", nodes)
        return nodes

    def pntr_assign(self):
        ...

    # --------------------------------- L_Array -------------------------------
    def array_size_qual(self):
        ...

    def array_creation(self):
        ...

    def subscript(self):
        ...

    def array_opd(self):
        ...

    def array_ref(self):
        ...

    def array_assign(self):
        ...

    # -------------------------------- L_Struct -------------------------------
    def struct_size_qual(self):
        ...

    def struct_creation(self):
        ...

    def attr(self):
        ...

    def struct_opd(self):
        ...

    def struct_ref(self):
        ...

    def struct_assign(self):
        ...

    def struct_decl_stmt(self):
        ...

    # -------------------------------- L_If_Else ------------------------------
    def if_without_else(self):
        ...

    def if_with_else(self):
        ...

    def if_else_stmt(self):
        ...

    # --------------------------------- L_Loop --------------------------------
    def while_(self):
        ...

    def do_while(self):
        ...

    def loop_stmt(self):
        ...

    # --------------------------------- L_Stmt --------------------------------
    def stmt(self, nodes):
        print("stmt", nodes)
        return nodes

    # ---------------------------------- L_Fun --------------------------------
    def fun_size_qual(self):
        ...

    def fun_call(self):
        ...

    def fun_opd(self):
        ...

    def return_(self):
        ...

    def fun_stmt(self):
        ...

    def def_(self, nodes):
        print("def_", nodes)
        return nodes

    # --------------------------------- L_File --------------------------------
    def file(self, nodes):
        print("file", nodes)
        return nodes


with open("./concrete_syntax.lark") as fin:
    parser = Lark(fin.read(), start="file")
    dt = parser.parse(
        r"""
        testus
        char test(){
            int var = ----10;  // das ist doof
            char pntr = *(var + 10);
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
    print(ast)
