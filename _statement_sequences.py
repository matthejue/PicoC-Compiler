from tokentypes import *  # pylint: disable=unused-wildcard-import

##########################################################################
#                        Statement sequences (code_ss)                   #
##########################################################################


def statement_sequence(self):
    """Sequence of Statements

    :returns: Subtree of this sequence of statemens

    """
    left_node, error = self.statement()

    if error:
        return None, error

    while T_SEMICOLON == self.current_tok.type:
        left_node, error = self.binary_op(left_node, self.statement)

        if error:
            return None, error

    return left_node, None


def statement(self):
    """Either a assignment, conditional or loop statement

    :returns: Subtree of this statement

    """
    if T_IDENTIFIER == self.current_char.type:
        return self.variable_assignment()
    # else if T_IF
    # else if T_WHILE
    # else if T_DO_WHILE
