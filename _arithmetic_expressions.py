from tokentypes import *  # pylint: disable=unused-wildcard-import

###############################################################################
#                           Arithmetic Expressions                            #
###############################################################################


def code_ae(self):
    """creates a arithmetic expression and considers operator precedence.
    :returns: arithmetic expression node.

    """
    expression, error = self.precedence_2()

    if error:
        return None, error
    elif T_EOF != self.current_tok.type:
        return None, SyntaxError(self.current_tok.md.copy(),
                                 "operator like '+', '-', '*', '/' etc.")
    return expression, None


def precedence_2(self):
    """Consider precedence rules level 2.
    :returns: Subtree of this operation.

    """
    left_node, error = self.precedence_1()

    if error:
        return None, error

    while T_PRECEDENCE_2 in self.current_tok.type:
        left_node, error = self.binary_op(left_node, self.precedence_1)

        if error:
            return None, error

    return left_node, None


def precedence_1(self):
    """Consider precedence rules level 1.
    :returns: Subtree of this operation.

    """
    left_node, error = self.arithmetic_operand()
    if error:
        return None, error

    while T_PRECEDENCE_1 in self.current_tok.type:
        left_node, error = self.binop(left_node, self.arithmetic_operand)

        if error:
            return None, error

    return left_node, None


def arithmetic_operand(self):
    """Creates a arithmetic expression.
    :returns: arithmetic expression node.

    """
    if T_UNOP in self.current_tok.type:
        return self.unary_op()
    elif [T_VARIABLE, T_CONSTANT, T_CONSTANT_IDENTIFIER] > [self.current_tok.type]:
        return self.leave()
    elif T_L_PAREN == self.current_tok.type:
        return self.parenthesis()

    return None, SyntaxError(self.current_tok.md.copy(), "operand like a \
                             constant, constant identifier or variable \
                             identifier")


def leave(self):
    """either variable, constant or constant identifier

    :returns: Leave with variable

    """
    node = LeaveNode(self.current_tok)
    self.next_tok()
    return node, None


def parenthesis(self):
    """Handles Parenthesis
    :returns: Subtree of the expression inside the parenthesis

    """
    self.next_tok()
    a_expr, error = self.precedence_2()

    if error:
        return None, error

    if T_R_PAREN != self.current_tok.type:
        return None, SyntaxError(self.current_tok.md.copy(), "')'")
    self.next_tok()
    return a_expr, None


def binary_op(self, left_node, expression):
    """Binary Operation.
    :returns: Subtree of this binary operation.

    """
    tok_operation = self.special_case_minus(T_BINOP)
    self.next_tok()
    right_node, error = expression()

    if error:
        return None, error

    return BinaryOpNode(left_node, tok_operation, right_node), None


def unary_op(self):
    """Unary Operation.
    :returns: Subtree with only one child.

    """
    tok_operation = self.special_case_minus(T_UNOP)
    self.next_tok()
    right_node, error = self.arithmetic_operand()

    if error:
        return None, error

    return UnaryOpNode(tok_operation, right_node), None


def special_case_minus(self, tokentype):
    """Minus has to be treated seperatly.
    :returns: potentially corrected Token for the unary operation.

    """
    if '-' == self.current_tok.md.value:
        if tokentype == T_UNOP:
            # to make the md.copy() work correctly
            self.current_tok.md.current_char = self.current_tok.md.value

            return Token(self.current_tok.type[0], self.current_tok.md.copy())
        elif tokentype == T_BINOP:
            return Token(self.current_tok.type[1:], self.current_tok.md.copy())
    else:
        return self.current_tok
