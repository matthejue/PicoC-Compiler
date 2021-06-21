from enum import Enum


class STEntryType(Enum):
    const_int = auto()
    const_char = auto()
    var_int = auto()
    var_char = auto()


class SymbolTable():

    """Table which contains the data location or values associated with
    identifiers"""

    def __init__(self, idx):
        self.symbols = dict()
        self.idx = idx

    def assign(self, identifier, value, entry_type):
        """Creates or reassigns a value to a identifier

        :returns: None

        """
        if entry_type in [STEntryType.const_int, STEntryType.const_char]:
            self.symbols[identifier] = [entry_type, value]
            return

        self.symbols[identifier] = [entry_type, self.idx]
        self.idx += 1

    def get(self, identifier):
        """Value of a identifier

        :returns: Value of identifier

        """
        return self.symbols[identifier]
