from enum import Enum


class ASTNode:

    """Abstract Syntax Tree holds the relevant Tokens and represents grammatical
    relationships the parser came across"""

    def __init__(self, token):
        self.token = token
        self.children = []

    def getNodeType(self):
        """

        :returns: None

        """
        return self.token.type

    def addChild(self, t):
        """

        :t: subtree
        :returns: None

        """
        self.children += [t]

    def isEmpty(self):
        return not self.token

    def __repr__(self):
        if not self.children:
            return str(self.token)
        acc = f"({self.token}"
        for child in self.children:
            acc += f" {child}"
        acc += ")"
        return acc


# class ArithExprNode(ASTNode):

    # """Abstract Syntax Tree for Arithmetic Expressions"""

    # def __init__(self):
        # super()__init__(self, token)
