from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from lexer import TT
from abstract_syntax_tree import ASTNode


class LogicExpressionGrammar(ArithmeticExpressionGrammar):

    """The logic expression part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_le(self):
        """logic expression startpoint

        :grammar: <not>
        :returns: None

        """
        self._and()

    def _or(self):
        """or

        :grammar: <and> (or <and>)*
        :returns: None

        """

    def _and(self):
        """and

        :grammar: <le> (and )*
        :returns: None

        """

    def _lo(self):
        """logic operand

        :grammar: <not>
        :returns: None

        """
        if self.LTT(1) == TT.NOT:
            self._not()
        elif self.LTT(1) == TT.L_PAREN:
            pass
        # la (12 < var etc.> und das verbunden mit le && etc.

    def _not(self):
        """not

        :grammar: !+<code_le>
        :returns: None

        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.NOT])

        while self.LTT(1) == TT.NOT:
            self.match_and_add(TT.NOT)

            self.ast_builder.down(savestate_node)

        self._code_le()

        self.ast_builder.up(savestate_node)
