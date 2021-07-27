from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT


class AssignmentGrammar(ArithmeticExpressionGrammar):
    """The assignment expression part of the context free grammer of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_a(self):
        """assignment expression

        :grammer: <va>
        :returns: None

        """
        self.va()

    def va(self):
        """variable assignment

        :grammer: #2 (<v> = #2)+ <e>
        :returns: None

        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.EQUALS])

        while True:
            self.match_and_add([TT.IDENTIFIER])
            self.match_and_add([TT.EQUALS])

            if self.LTT(2) != TT.EQUALS:
                break

            self.ast_builder.down(ASTNode, [TT.EQUALS])

        self.code_ae()

        self.ast_builder.up(savestate_node)
