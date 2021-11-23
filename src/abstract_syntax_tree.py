# from enum import Enum
from lexer import Token, TT
from code_generator import CodeGenerator
from symbol_table import SymbolTable, VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError


class TokenNode:

    """Abstract Syntax Tree Node for Leaves"""

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

    def visit(self, ):
        # in case the AssignmentNode doesn't have a AllocationNode as first
        # child there'll be a TokenNode which needs a dummy visit() function as
        # there's polymorphic visit() call
        pass


class ASTNode(TokenNode):

    """Node of a Normalized Heterogeneous Abstract Syntax Tree (AST), partially
    also has some different Normalized Heterogeneous AST Nodes. A AST holds the
    relevant Tokens and represents grammatical relationships the parser came
    across.  Homogeneous AST means having only one node type and all childs
    normalized in a list. Normalized Heterogeneous means different Node types
    and all childs normalized in a list"""

    def __init__(self, tokentypes):
        # at the time of creation the tokenvalue is unknown
        self.children = []
        # the first tokentype is always the actual tokentype and the others are
        # for symbols like e.g. '-' which had to get a seperate tokentype
        # because they overlap with e.g. unary and binary operations
        super().__init__(Token(tokentypes[0], None, None))
        self.tokentypes = tokentypes
        # decide whether a node should be ignored and just show his children if
        # he has any
        self.ignore = True
        self.code_generator = CodeGenerator()
        self.symbol_table = SymbolTable()

    def _is_tokennode(self, node):
        """checks if something is a TokenNode

        :returns: boolean
        """
        # being not instance of ASTNode means being instance of TokenNode
        return not isinstance(node, ASTNode)

    def addChild(self, node):
        """

        :returns: None
        """
        # in case the representative tokens of self appear as attribute of a
        # TokenNode, the token of self can finally register the right value
        # Because of e.g. <alloc>: <word> <word> ... one should only take the
        # first TokenNode matching the possible representative tokens
        if self._is_tokennode(node) and node.token.type in\
                self.tokentypes:
            self.token.value = node.token.value
            self.token.position = node.token.position
            self.ignore = False
            return

        self.children += [node]

    def show_generated_code(self, ):
        return self.code_generator.show_code()

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


def strip_multiline_string(mutline_string):
    """helper function to make mutlineline string usable on different
    indent levels

    :grammar: grammar specification
    :returns: None
    """
    mutline_string = [i.lstrip() for i in mutline_string.split('\n')]
    mutline_string.pop()
    mutline_string_acc = ""
    for line in mutline_string:
        mutline_string_acc += line + '\n'
    return mutline_string_acc
