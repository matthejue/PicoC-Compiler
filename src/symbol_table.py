from ast_node import ASTNode
from picoc_nodes import N
import global_vars
from global_funs import convert_to_single_line

# ------------------------------- L_Symbol_Table ------------------------------
class ST:
    class Empty(ASTNode):
        pass

    class BuiltIn(ASTNode):
        pass

    class SelfDeclared(ASTNode):
        pass

    class Pos(ASTNode):
        def __init__(self, line, column):
            self.line = line
            self.column = column
            super().__init__(visible=[self.line, self.column])

    class Symbol(ASTNode):
        def __init__(
            self,
            type_qual=None,
            datatype=None,
            name=None,
            val_addr=None,
            pos=None,
            size=None,
        ):
            self.type_qual = type_qual if type_qual else ST.Empty()
            self.datatype = datatype if datatype else ST.Empty()
            self.name = name if name else ST.Empty()
            self.val_addr = val_addr if val_addr else ST.Empty()
            self.pos2 = pos if pos else ST.Empty()
            self.size = size if size else ST.Empty()

        __match_args__ = ("type_qual", "datatype", "name", "val_addr", "pos", "size")

        def __repr__(self, depth=0):
            tmp = global_vars.args.verbose
            global_vars.args.verbose = True
            acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}"
            acc += "\n    {"
            acc += "\n      type qualifier:   " + convert_to_single_line(self.type_qual)
            acc += "\n      datatype:         " + convert_to_single_line(self.datatype)
            acc += "\n      name:             " + convert_to_single_line(self.name)
            acc += "\n      value or address: " + convert_to_single_line(self.val_addr)
            acc += "\n      position:         " + convert_to_single_line(self.pos2)
            acc += "\n      size:             " + convert_to_single_line(self.size)
            global_vars.args.verbose = tmp
            acc += "\n    }"
            return acc + ("\n  )" if global_vars.args.verbose else "")

    class SymbolTable(ASTNode):
        def __init__(self):
            self.symbols = dict()
            self._init_type_sytem()
            super().__init__(visible=[self.symbols])

        def _init_type_sytem(self):
            self.define(ST.Symbol(datatype=ST.BuiltIn(), name=N.Name("char")))
            self.define(ST.Symbol(datatype=ST.BuiltIn(), name=N.Name("int")))

        def define(self, symbol):
            self.symbols[symbol.name.val] = symbol

        def resolve(self, name):
            return self.symbols[name]
