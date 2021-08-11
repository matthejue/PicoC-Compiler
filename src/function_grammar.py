from src.statement_sequence_grammar import StatementSequenceGrammar
from src.abstract_syntax_tree import ASTNode
from src.lexer import TT

# TODO: Grammar irgendwo als oberste Grammar noch einrichten


class FunctionGrammar(StatementSequenceGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def code_f(self):
        """function grammar startpoint

        :grammar: <f>
        :returns: None

        """
        self.ast_builder.down(ASTNode, [TT.FUNCTION])

        # little heck to make the second statement visible, TODO: remove it
        # later
        self.ast_builder.current_node.token.value = "my_function"
        self.ast_builder.current_node.ignore = False

        self.code_ss()
