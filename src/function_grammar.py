# from assignment_allocation_grammar import AssignmentAllocationGrammar
from statement_sequence_grammar import StatementSequenceGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT

# TODO: FunctionGrammar zu Grammar umbennenen


# class FunctionGrammar(AssignmentAllocationGrammar):
class FunctionGrammar(StatementSequenceGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def start_parse(self):
        """start parsing the grammar

        :returns: None

        """
        self.ast_builder.down(ASTNode, [TT.FUNCTION])
        self.code_ss()
        # self.code_aa()

        # little check to make the second statement visible, TODO: remove it
        # later
        self.ast_builder.current_node.token.value = "my_function"
