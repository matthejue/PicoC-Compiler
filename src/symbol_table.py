from ast_node import ASTNode
import picoc_nodes as pn
import global_vars
from util_funs import convert_to_single_line
from colormanager import ColorManager as CM

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
        acc = f"\n    {CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}"
        acc += f"\n      {CM().CYAN}{{{CM().RESET}"
        acc += (
            f"\n        {CM().GREEN}type qualifier{CM().RESET}:         "
            + convert_to_single_line(self.type_qual)
        )
        acc += (
            f"\n        {CM().GREEN}datatype{CM().RESET}:               "
            + convert_to_single_line(self.datatype)
        )
        acc += (
            f"\n        {CM().GREEN}name{CM().RESET}:                   "
            + convert_to_single_line(self.name)
        )
        acc += (
            f"\n        {CM().GREEN}value or address{CM().RESET}:       "
            + convert_to_single_line(self.val_addr)
        )
        acc += (
            f"\n        {CM().GREEN}position{CM().RESET}:               "
            + convert_to_single_line(self.pos2)
        )
        acc += (
            f"\n        {CM().GREEN}size{CM().RESET}:                   "
            + convert_to_single_line(self.size)
        )
        acc += f"\n      {CM().CYAN}}}{CM().RESET}"
        return acc + ("\n    )" if global_vars.args.double_verbose else "")


class SymbolTable(ASTNode):
    def __init__(self):
        self.symbols = dict()
        self._init_type_sytem()
        super().__init__(visible=[self.symbols])

    def _init_type_sytem(self):
        if global_vars.args.double_verbose:
            self.declare(Symbol(datatype=BuiltIn(), name=pn.Name("char")))
            self.declare(Symbol(datatype=BuiltIn(), name=pn.Name("int")))

    def exists(self, name):
        return self.symbols.get(name)

    def declare(self, symbol):
        self.symbols[symbol.name.val] = symbol

    def resolve(self, name):
        return self.symbols[name]
