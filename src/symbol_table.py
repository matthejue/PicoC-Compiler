from ast_node import ASTNode
from picoc_nodes import N

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

    class Symbol(ASTNode):
        def __init__(
            self,
            type_qual=None,
            datatype=None,
            name=None,
            val=None,
            pos=None,
            size=None,
        ):
            self.type_qual = type_qual if type_qual else ST.Empty()
            self.datatype = datatype if datatype else ST.Empty()
            self.name = name if name else ST.Empty()
            self.val = val if val else ST.Empty()
            self.pos = pos if pos else ST.Empty()
            self.size = size if size else ST.Empty()

        __match_args__ = ("type_qual", "datatype", "name", "val", "pos", "size")

    class SymbolTable(ASTNode):
        def __init__(self):
            self.symbols = dict()
            self._init_type_sytem()

        def _init_type_sytem(self):
            self.define(ST.Symbol(datatype=ST.BuiltIn(), name=N.Name("char")))
            self.define(ST.Symbol(datatype=ST.BuiltIn(), name=N.Name("int")))

        def define(self, symbol):
            self.symbols[symbol.name.val] = symbol

        def resolve(self, name):
            return self.symbols[name]
