from enum import Enum


class ASTNode:

    """Abstract Syntax Tree holds the relevant Tokens and represents grammatical
    relationships the parser came across"""

    def __init__(self, token):
        # TODO: rename it to t_or_tt
        self.token = token
        self.children = []

    def getNodeType(self):
        """

        :returns: None

        """
        return self.token.type

    def addChild(self, token_or_node):
        """

        :t: subtree
        :returns: None

        """
        self.children += [token_or_node]

    def isEmpty(self):
        return not self.token

    def __repr__(self):
        if len(self.children) == 1:
            return f"{self.children[0]}"

        acc = f"({self.token}"
        for child in self.children:
            acc += f" {child}"
        acc += ")"
        return acc


# class ArithExprNode(ASTNode):

    # """Abstract Syntax Tree for Arithmetic Expressions"""

    # def __init__(self):
        # super()__init__(self, token)
