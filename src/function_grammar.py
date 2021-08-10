from statement_sequence_grammar import StatementSequenceGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT

# TODO: Grammar irgendwo als oberste Grammar noch einrichten


class FunctionGrammar(StatementSequenceGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def start_parse(self):
        """start parsing the grammar

        :returns: None

        """
        self.ast_builder.down(ASTNode, [TT.FUNCTION])

        # little heck to make the second statement visible, TODO: remove it
        # later
        self.ast_builder.current_node.token.value = "my_function"
        self.ast_builder.current_node.ignore = False

        self.code_ss()
