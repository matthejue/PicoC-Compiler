from ast_node import ASTNode
import picoc_nodes as pn
import global_vars
from global_funs import convert_to_single_line

# ------------------------------- L_Symbol_Table ------------------------------
class Empty(ASTNode):
    pass


class BuiltIn(ASTNode):
    pass


class Pos(ASTNode):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        super().__init__(visible=[self.line, self.column])

    __match_args__ = ("line", "column")


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
        self.type_qual = type_qual if type_qual else Empty()
        self.datatype = datatype if datatype else Empty()
        self.name = name if name else Empty()
        self.val_addr = (
            val_addr if val_addr else [] if isinstance(val_addr, list) else Empty()
        )
        self.pos2 = pos if pos else Empty()
        self.size = size if size else Empty()

    __match_args__ = ("type_qual", "datatype", "name", "val_addr", "pos2", "size")

    def __repr__(self, depth=0):
        tmp = global_vars.args.double_verbose
        global_vars.args.double_verbose = True
        acc = f"\n    {self.__class__.__name__}{'(' if global_vars.args.double_verbose else ' '}"
        acc += "\n      {"
        acc += "\n        type qualifier:         " + convert_to_single_line(
            self.type_qual
        )
        acc += "\n        datatype:               " + convert_to_single_line(
            self.datatype
        )
        acc += "\n        name:                   " + convert_to_single_line(self.name)
        acc += "\n        value or address:       " + convert_to_single_line(
            self.val_addr
        )
        acc += "\n        position:               " + convert_to_single_line(self.pos2)
        acc += "\n        size:                   " + convert_to_single_line(self.size)
        global_vars.args.double_verbose = tmp
        acc += "\n      }"
        return acc + ("\n    )" if global_vars.args.double_verbose else "")


class SymbolTable(ASTNode):
    def __init__(self):
        self.symbols = dict()
        self._init_type_sytem()
        super().__init__(visible=[self.symbols])

    def _init_type_sytem(self):
        if global_vars.args.double_verbose:
            self.define(Symbol(datatype=BuiltIn(), name=pn.Name("char")))
            self.define(Symbol(datatype=BuiltIn(), name=pn.Name("int")))

    def exists(self, name):
        return self.symbols.get(name)

    def define(self, symbol):
        self.symbols[symbol.name.val] = symbol

    def resolve(self, name):
        return self.symbols[name]
