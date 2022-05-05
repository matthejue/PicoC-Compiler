from code_generator import CodeGenerator
from symbol_table import SymbolTable
import global_vars


class ASTNode:
    """Node of a Normalized Heterogeneous Abstract Syntax Tree (AST), partially
    also has some different Normalized Heterogeneous AST Nodes. A AST holds the
    relevant Tokens and represents grammatical relationships the parser came
    across.  Homogeneous AST means having only one node type and all childs
    normalized in a list. Normalized Heterogeneous means different Node types
    and all childs normalized in a list"""

    def __init__(self, value=None, position=(-1, -1), children=[]):
        """
        :tokentype: list of TT's, first entry will be the TT of the Node
        """
        self.value = value
        self.position = position
        self.children = children

    def update_match_args(self):
        pass

    __match_args__ = ("value", "position")

    def __repr__(self):
        global_vars.show_node = False
        return self.to_string()

    def to_string(self):
        if not self.children:
            if not self.value:
                return f"{self.__class__.__name__}()"
            if global_vars.args.verbose:
                return f"{self.__class__.__name__}('{self.value}')"
            return f"'{self.value}'"

        acc = ""

        if global_vars.args.verbose or global_vars.show_node:
            acc += self.__class__.__name__

        acc += f"({self.children[0]}"

        for child in self.children[1:]:
            acc += f" {child}"

        return acc + ")"

    def to_string_show_node(self):
        global_vars.show_node = True
        tmp = self.to_string()
        global_vars.show_node = False
        return tmp
