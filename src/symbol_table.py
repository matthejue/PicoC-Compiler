class Symbol:
    def __init__(self, type_qual="-", datatype="-", name="-", val="-", pos="-"):
        self.type_qual = type_qual
        self.datatype = datatype
        self.name = name
        self.val = val
        self.pos = pos

    __match_args__ = ("type_qual", "datatype", "name", "val", "pos")

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
                + ">"
            )
        return self.name


class SymbolTable:
    def __init__(self):
        self.symbols = dict()
        self._init_type_sytem()

    def _init_type_sytem(self):
        self.define(Symbol(type_qual="BuiltIn", name="char"))
        self.define(Symbol(type_qual="BuiltIn", name="int"))

    def define(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def resolve(self, name) -> Symbol:
        return self.symbols[name]

    def __repr__(self):
        return str(self.symbols)
