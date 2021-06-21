from errors import SyntaxError

# TODO: later for initialization needed
from symbol_table import STEntryType
import globals

##########################################################################
#                Allocation / Assignment expressions (code_aa)           #
##########################################################################


def variable_assignment(self):
    """Assigns what's on the right side to the variable on the left side

    :sreturns: Binary subtree with the Assignment

    """

    left_node = self.leave()

    while T_EQUAL == self.current_tok:
        left_node, error = self.binary_op(left_node, self.code_ae)

        if error:
            return None, error

    return left_node, None


# def initialization(self):
    # """TODO: Docstring for initialization.

    # :function: TODO
    # :returns: TODO

    # """
    # pass
