from code_generator import CodeGenerator
from symbol_table import SymbolTable


class ASTNode:
    """Node of a Normalized Heterogeneous Abstract Syntax Tree (AST), partially
    also has some different Normalized Heterogeneous AST Nodes. A AST holds the
    relevant Tokens and represents grammatical relationships the parser came
    across.  Homogeneous AST means having only one node type and all childs
    normalized in a list. Normalized Heterogeneous means different Node types
    and all childs normalized in a list"""
    def __init__(self, value=None, position=None):
        """
        :tokentype: list of TT's, first entry will be the TT of the Node
        """
        self.children = []
        self.value = value
        self.position = position
        self.code_generator = CodeGenerator()
        self.symbol_table = SymbolTable()

    __match_args__ = ("value", "position")

    def add_child(self, node):
        """
        :returns: None
        """
        self.children += [node]

    def show_generated_code(self, ):
        return self.code_generator.show_code()

    def update_match_args(self, ):
        pass

    def __repr__(self):
        if not self.children:
            return self.value

        acc = "(" + f"{self.children[0]}"

        for child in self.children[1:]:
            acc += f" {child}"

        return acc + ")"


def strip_multiline_string(mutline_string):
    """helper function to make mutlineline string usable on different
    indent levels

    :grammar: grammar specification
    :returns: None
    """
    mutline_string = ''.join(
        [i.lstrip() + '\n' for i in mutline_string.split('\n')[:-1]])
    # every code piece ends with \n, so the last element can always be poped
    return mutline_string
