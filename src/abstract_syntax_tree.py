from enum import Enum
from lexer import Token


class TokenNode:

    """Abstract Syntax Tree for Arithmetic Expressions"""

    def __init__(self, token):
        self.token = token

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

    def __init__(self, tokentypes):
        # at the time of creation the tokenvalue is unknown
        self.children = []
        # the first tokentype is always the actual tokentype and the others are
        # for symbols like e.g. '-' which had to get a seperate tokentype
        # because they overlap with e.g. unary and binary operations
        super().__init__(Token(tokentypes[0], None))
        self.tokentypes = tokentypes

    def addChild(self, node):
        """

        :t: subtree
        :returns: None

        """
        # in case the representative token of self appears as attribute of a
        # TokenNode, the token of self can finally register the right value
        # being not instance of ASTNode means being instance of TokenNode
        if not isinstance(node, ASTNode) and \
                node.token.type in self.tokentypes:
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
