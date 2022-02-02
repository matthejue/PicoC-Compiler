import global_vars


class Symbol:
    """Name for a program entity like a variable or function"""

    __match_args__ = ("value", "datatype")

    def __init__(self, name, datatype, position, value):
        """
        :name: string
        :datatype: Symbol
        :position: tuple(int, int)
        :value: string
        """
        self.name = name
        self.datatype = datatype
        self.position = position
        self.value = value

    def get_name(self, ):
        return self.name

    def __repr__(self, ):
        if self.datatype != '/':
            return '<' + self.name + ':' + str(
                self.datatype) + ':' + self.value + '>'
        return self.name


class VariableSymbol(Symbol):
    """Represents a variable definition (name, datatype) in symbol table"""
    def __init__(self, name, datatype, position):
        super().__init__(name, datatype, position, '/')

    def get_type(self, ):
        return "variable"


class ConstantSymbol(Symbol):
    """Represents a variable definition (name, datatype) in symbol table"""
    def __init__(self, name, datatype, position):
        super().__init__(name, datatype, position, '/')

    def get_type(self, ):
        return "named constant"


class BuiltInTypeSymbol(Symbol):
    """Built in datatypes such as int and char"""

    __match_args__ = ("name", )

    def __init__(self, name):
        super().__init__(name, '/', '/', '/')

    def get_type(self, ):
        return "built in"


class Scope:
    """Code region with with a well-defined boundary which groups symbol
    definitions"""
    def __init__(self, ):
        """

        :fa_pointer: free address pointer
        :returns: None
        """
        self.symbols = dict()

    def get_scope_name(self, ):
        """
        :return: string
        """
        return "global"

    def get_enclosing_scope(self, ):
        """
        :return: Scope
        """
        return None

    def define(self, sym):
        """define sym in this scope

        :sym: Symbol
        :return: None
        """
        self.symbols[sym.name] = sym

    def resolve(self, name) -> Symbol:
        """look up name in scope

        :name: string
        :return: Symbol
        """
        return self.symbols[name]


class _SymbolTable(Scope):
    """Datastructure that tracks language symbols"""

    _instance = None

    def __init__(self):
        super().__init__()
        self.initTypeSystem()
        self.fa_pointer = global_vars.args.begin_data_segment

    def initTypeSystem(self, ):
        self.define(BuiltInTypeSymbol('char'))
        self.define(BuiltInTypeSymbol('int'))

    def allocate(self, sym):
        """Determine address of variable

        :returns: string of adress
        """
        if self.symbols[sym.name].value == "/":
            self.symbols[sym.name].value = str(self.fa_pointer)
            self.fa_pointer += 1
            return str(self.fa_pointer - 1)
        return -1

    def __repr__(self, ):
        return self.get_scope_name() + ":" + str(self.symbols)


def SymbolTable():
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if not _SymbolTable._instance:
        _SymbolTable._instance = _SymbolTable()
    return _SymbolTable._instance
