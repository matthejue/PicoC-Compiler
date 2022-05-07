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

    __match_args__ = ("value", "position")

    def __repr__(self, depth=0):
        if not self.children:
            if not self.value:
                return f"\n{' ' * depth}{self.__class__.__name__}"
            return f"\n{' ' * depth}{self.__class__.__name__}('{self.value}')"

        acc = ""

        if depth > 0:
            acc += f"\n{' ' * depth}{self.__class__.__name__}"
        else:
            acc += f"{' ' * depth}{self.__class__.__name__}"

        for child in self.children:
            if isinstance(child, list):  # in case of []
                if not child:
                    acc += f"\n{' ' * (depth+2)}[]"
                    continue
                acc += f"\n{' ' * (depth + 2)}["
                for child_child in child:
                    acc += f"{child_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
                continue
            acc += f"{child.__repr__(depth+2)}"

        return acc
