###############################################################################
#                                 Tree Nodes                                  #
###############################################################################


class BinaryNode:
    """Node for a binary operation."""

    def __init__(self, left_node, tok, right_node):
        self.left_node, self.tok, self.right_node = left_node, tok, right_node

    def __repr__(self):
        return f'({self.left_node}, {self.tok}, {self.right_node})'


class UnaryNode:
    """Node for a unary operation."""

    def __init__(self, tok, right_node):
        self.tok, self.right_node = tok, right_node

    def __repr__(self):
        return f'({self.tok}, {self.right_node})'


class LeaveNode:
    """Node for a Number."""

    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

###############################################################################
#                                   Parser                                    #
###############################################################################


class Parser:
    """Builds up a syntax tree from the tokens created by the lexer. The tree
    does exactly tell which operations have to be performed in which order.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.next_tok()

    def next_tok(self):
        """Goes to the next_tok token.
        :returns: None.

        """
        self.tok_idx += 1
        self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        """Creates the syntax from the tokens created by the lexer.
        :returns: rootnode of sub-syntax tree.

        """
        code_ae, error = self.code_ae()
        return code_ae, error

    from _arithmetic_expressions import code_ae, arithmetic_operand, unary_op, \
        constant, binary_op, special_case_minus, precedence_1, precedence_2, \
        parenthesis
