from enum import Enum
from lexer import Token
import globals


class TokenNode:

    """Abstract Syntax Tree for Arithmetic Expressions"""

    def __init__(self, tokentype):
        self.token = Token(tokentype, None)

    def getNodeType(self):
        """

        :returns: None

        """
        return self.token.type

    def isEmpty(self):
        return not self.token

    def __repr__(self):
        return f"{self.token}"


class ASTNode(TokenNode):

    """Abstract Syntax Tree holds the relevant Tokens and represents grammatical
    relationships the parser came across"""

    def __init__(self, tokentype):
        # at the time of creation the tokenvalue is unknown
        self.children = []
        super().__init__(tokentype)

    def addChild(self, node):
        """

        :t: subtree
        :returns: None

        """
        if self.token.type == node.token.type:
            self.token.value = node.token.value
            return
        self.children += [node]

    def __repr__(self):
        # if Node doesn't even reach it's own operation token it's unnecessary
        # and should be skipped
        if not self.children:
            return f"{self.token}"
        elif not self.token.value:
            return f"{self.children[0]}"

        acc = f"({self.token}"

        for child in self.children:
            acc += f" {child}"

        acc += ")"
        return acc


class Prec1Node(ASTNode):

    """Abstract Syntax Tree for Arithmetic Expressions"""

    def __init__(self, token):
        super().__init__(self, token)
