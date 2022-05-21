from ast_node import ASTNode

# ------------------------------- L_SymbolTable ------------------------------
class ST:
    class Empty(ASTNode):
        pass

    class Symbol(ASTNode):
        def __init__(
            self, type_qual=Empty(), datatype="-", name="-", val="-", pos="-", size="-"
        ):
            self.type_qual = type_qual
            self.datatype = datatype
            self.name = name
            self.val = val
            self.pos = pos
            self.size = size

        __match_args__ = ("type_qual", "datatype", "name", "val", "pos", "size")

        def __repr__(self):
            if self.datatype != "-":
                return (
                    "<"
                    + self.type_qual
                    + ":"
                    + self.datatype
                    + ":"
                    + self.name
                    + ":"
                    + self.val
                    + ":"
                    + self.pos
                    + ":"
                    + self.size
                    + ">"
                )
            return self.name

    class SymbolTable(ASTNode):
        def __init__(self):
            self.symbols = dict()
            self._init_type_sytem()

        def _init_type_sytem(self):
            self.define(ST.Symbol(type_qual="BuiltIn", name="char"))
            self.define(ST.Symbol(type_qual="BuiltIn", name="int"))

        def define(self, symbol: Symbol):
            self.symbols[symbol.name.val] = symbol

        def resolve(self, name) -> Symbol:
            return self.symbols[name]

        def __repr__(self):
            return str(self.symbols)
