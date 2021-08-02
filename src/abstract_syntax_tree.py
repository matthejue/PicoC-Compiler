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

    """Abstract Syntax Tree holds the relevant Tokens and represents
    grammatical relationships the parser came across"""

    def __init__(self, tokentypes):
        # at the time of creation the tokenvalue is unknown
        self.children = []
        # the first tokentype is always the actual tokentype and the others are
        # for symbols like e.g. '-' which had to get a seperate tokentype
        # because they overlap with e.g. unary and binary operations
        super().__init__(Token(tokentypes[0], None))
        self.tokentypes = tokentypes
        # decide whether a node should be ignored and just show his children if
        # he has any
        self.ignore = True

    def addChild(self, node):
        """

        :returns: None

        """
        # in case the representative tokens of self appear as attribute of a
        # TokenNode, the token of self can finally register the right value
        # being not instance of ASTNode means being instance of TokenNode.
        # Because of e.g. <alloc>: <word> <word> ... one should only take the
        # first TokenNode matching the possible representative tokens
        if not self.token.value and not isinstance(node, ASTNode) and \
                node.token.type in self.tokentypes:
            self.token.value = node.token.value
            self.ignore = False
            return

        self.children += [node]

    def __repr__(self):
        # if Node doesn't even reach it's own operation token it's unnecessary
        # and should be skipped
        if not self.children:
            return f"{self.token}"
        # TODO: swap the order of this conditional statements when finishing
        # the project because if a node isn't activated it should never be
        # seen, it's just useful for debugging to have it the other way round
        elif self.ignore:
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
