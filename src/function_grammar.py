from assignment_grammar import AssignmentGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT

# TODO: FunctionGrammar zu Grammar umbennenen


class FunctionGrammar(AssignmentGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def start_parse(self):
        """start parsing the grammar

        :returns: None

        """
        self.ast_builder.down(ASTNode, [TT.ROOT])
        self.code_a()
