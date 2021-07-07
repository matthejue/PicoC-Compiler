from enum import Enum, auto


class STEntryType(Enum):
    const_int = auto()
    const_char = auto()
    var_int = auto()
    var_char = auto()

##########################################################################
#                                Symbol table                            #
##########################################################################


class SymbolTable():

    """Table which contains the type, location or value associated with
    identifiers"""

    def __init__(self, idx):
        """
        structure of entries in the symbols dictionary:
        {identifier: [entry_type, address (variable) / value (constant)]}

        """
        self.symbols = dict()
        self.idx = idx

    def register(self, identifier, entry_type):
        """Registers constants and variables and allocates space for variables.

        :returns: None

        """
        # constants don't have a address in memory
        if entry_type in [STEntryType.const_int, STEntryType.const_char]:
            self.symbols[identifier] = [entry_type, None]

        # variables have a address in memory and need to be allocated
        self.symbols[identifier] = [entry_type, self.idx]
        self.idx += 1

    def assign_constant(self, identifier, value):
        """Assigns value to constant in the code generation phase

        :returns: None

        """
        if not identifier in self.symbols:
            # error if identifier is not yet allocated
            # TODO: error if identifier is not yet allocated
            pass
        elif self.symbols[identifier][1]:
            # error if constant gets a value assigned more than once
            # TODO: error if constants gets a value assigned more than once
            pass
        self.symbols[identifier][1] = value

    def get(self, identifier):
        """Value of a identifier

        :returns: Type and value of identifier

        """
        return self.symbols[identifier]
