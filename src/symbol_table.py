import global_vars


class Symbol:

    """Name for a program entity like a variable or function"""

    def __init__(self, name, type, position, value):
        self.name = name
        self.type = type
        self.position = position
        self.value = value

    def get_name(self, ):
        return self.name

    def __repr__(self, ):
        if self.type:
            return '<' + self.name + ':' + self.type + '>'
        return self.name


class VariableSymbol(Symbol):

    """Represents a variable definition (name, type) in symbol table"""

    def __init__(self, name, type, position):
        super().__init__(name, type, position, None)


class ConstantSymbol(Symbol):

    """Represents a variable definition (name, type) in symbol table"""

    def __init__(self, name, type, position, value):
        super().__init__(name, type, position, value)


class BuiltInTypeSymbol(Symbol):

    """Built in types such as int and char"""

    def __init__(self, name):
        super().__init__(name, None, None, None)


class Scope:

    """Code region with with a well-defined boundary which groups symbol
    definitions"""

    def __init__(self, ):
        """

        :fa_pointer: free address pointer
        :returns: None
        """
        self.symbols = dict()  # {}

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

    def __init__(self):
        super().__init__()
        self.initTypeSystem()
        self.fa_pointer = global_vars.args.start_data_segment

    def initTypeSystem(self, ):
        self.define(BuiltInTypeSymbol('int'))
        self.define(BuiltInTypeSymbol('char'))

    def allocate(self, sym):
        if not self.symbols[sym.name].value:
            self.symbols[sym.name].value = self.fa_pointer
            self.fa_pointer += 1

    def __repr__(self, ):
        return self.get_scope_name() + ":" + self.symbols


def SymbolTable():
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if _SymbolTable._instance is None:
        _SymbolTable._instance = _SymbolTable()
    return _SymbolTable._instance
