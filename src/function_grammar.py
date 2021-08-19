from statement_sequence_grammar import StatementSequenceGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT

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
        self.ast_builder.current_node.token.value = "fun"
        self.ast_builder.current_node.ignore = False

        # TODO: Don't forget to remove this improvised conditional breakpoint
        if self.lexer.input == "if (var == 0) { var == 100; cars = cars + 1; } else { var = var - 1; b = 1; }":
            if self.lexer.input == "if (var == 0) { var == 100; cars = cars + 1; } else { var = var - 1; b = 1; }":
                pass
        self.code_ss()
