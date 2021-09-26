class Symbol:

    """Name for a program entity like a variable or function"""

    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        self.address = None

    def get_name(self, ):
        return self.name

    def set_address(self, address):
        self.address = address

    def get_address(self,):
        return self.address

    def __repr__(self, ):
        if self.type:
            return '<' + self.get_name() + ':' + self.type + '>'
        return self.get_name()


class VariableSymbol(Symbol):

    """Represents a variable definition (name, type) in symbol table"""

    def __init__(self, name, type):
        super().__init__(name, type)


class BuiltInTypeSymbol(Symbol):

    """Built in types such as int and char"""

    def __init__(self, name):
        super().__init__(name)


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

    def resolve(self, name):
        """look up name in scope

        :return: Symbol
        """
        return self.symbols[name]


class _SymbolTable(Scope):

    """Datastructure that tracks language symbols"""

    _instance = None

    def __init__(self, address):
        super().__init__()
        self.initTypeSystem()
        self.fa_pointer = address

    def initTypeSystem(self, ):
        self.define(BuiltInTypeSymbol('int'))
        self.define(BuiltInTypeSymbol('char'))

    def allocate(self, sym):
        if not self.symbols[sym.name].address:
            self.symbols[sym.name].set_address(self.fa_pointer)
            self.fa_pointer += 1

    def new(self, address=100):
        self.symbols = {}
        self.fa_pointer = address
        self.initTypeSystem()

    def __repr__(self, ):
        return self.get_scope_name() + ":" + self.symbols


def SymbolTable(address=100):
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if _SymbolTable._instance is None:
        _SymbolTable._instance = _SymbolTable(address)
    return _SymbolTable._instance
