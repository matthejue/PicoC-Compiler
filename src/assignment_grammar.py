from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT


class AssignmentGrammar(ArithmeticExpressionGrammar):
    """The assignment expression part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_a(self):
        """assignment expression

        :grammar: <va>
        :returns: None

        """
        self.va()

    def va(self):
        """variable assignment

        :grammar: #2 (<word> = #2)+ <ae>
        :returns: None

        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.EQUALS])

        while True:
            self.match_and_add([TT.WORD])
            self.match_and_add([TT.EQUALS])

            if self.LTT(2) != TT.EQUALS:
                break

            self.ast_builder.down(ASTNode, [TT.EQUALS])

        self.code_ae()

        self.ast_builder.up(savestate_node)

    def init(self):
        """initialisation of a variable

        :grammar: <word> <word> = <ae>
        :returns: None

        """
        # TODO: Testen, ob int var = zar = 12 funktioniert
        self.match_and_add([TT.WORD])
        self.match_and_add([TT.WORD])
