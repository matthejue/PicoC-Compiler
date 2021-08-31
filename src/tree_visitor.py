from lexer import TT


class ExternalTreeVisitor(object):

    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class"""

    def visit(self, node):
        tokentype = n.token.type
        if tokentype == TT.MAIN:

        elif tokentype == TT.FUNCTION:

    ROOT = "ROOT"
    EOF = "EOF"
    NUMBER = "number"
    IDENTIFIER = "word"
    UNARY_OP = "unary operator"
    BINOP_PREC_1 = "binary operator with precedence 1"
    BINOP_PREC_2 = "binary operator with precedence 2"
    ASSIGNMENT = "="
    L_PAREN = "("
    R_PAREN = ")"
    L_BRACE = "{"
    R_BRACE = "}"
    SEMICOLON = ";"
    MINUS = "-"
    ALLOC = "allocation"
    STATEMENT = "statement"
    FUNCTION = "function"
    NOT = "not operator or not as part of logical expression grammar"
    AND_OP = "and operator"
    OR_OP = "or operator"
    AND = "and as part of logical expression grammar"
    OR = "or as part of logical expression grammar"
    COMP_OP = "comparison operator"
    BITSHIFT = "bitshift"
    PRIM_DT = "primitive datatype"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO_WHILE = "do while"
    MAIN = "main"
