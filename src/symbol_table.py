from ast_node import ASTNode
from picoc_nodes import N
import global_vars

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
            acc += "\n      type qualifier:   " + "".join(
                list(map(lambda line: line.lstrip(), str(self.type_qual).split("\n")))
            )
            acc += "\n      datatype:         " + "".join(
                list(map(lambda line: line.lstrip(), str(self.datatype).split("\n")))
            )
            acc += "\n      name:             " + "".join(
                list(map(lambda line: line.lstrip(), str(self.name).split("\n")))
            )
            acc += "\n      value or address: " + "".join(
                list(map(lambda line: line.lstrip(), str(self.val_addr).split("\n")))
            )
            acc += "\n      position:         " + "".join(
                list(map(lambda line: line.lstrip(), str(self.pos2).split("\n")))
            )
            acc += "\n      size:             " + "".join(
                list(map(lambda line: line.lstrip(), str(self.size).split("\n")))
            )
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
