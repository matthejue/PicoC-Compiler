from lexer import TT
from errors import Errors
from if_else_nodes import If, IfElse
from dummy_nodes import NT
#  from statement_grammar import StatementGrammar


class IfElseGrammar:
    def code_ie(self, ):
        self.code_if_if_else()

    def code_if_if_else(self):
        """if or if else

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) (else ({
        <code_ss> }|<s>))?
        """
        errors = []
        if self.taste(self._taste_consume_if_without_else, errors):
            self._taste_consume_if_without_else()
        elif self.taste(self._if_else, errors):
            self._if_else()
        else:
            self._handle_all_tastes_unsuccessful("if or if else statement",
                                                 errors)

    def _taste_consume_if_without_else(self):
        """taste whether the next expression is a if without else

        :grammar: <if_without_else>
        """
        self._if_without_else()
        if self.LTT(1) == TT.ELSE:
            raise Errors.TastingError()

    def _if_without_else(self, ):
        """if

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>)
        """
        savestate_node = self.ast_builder.down(If)

        self._if_condition()
        self._branch()

        self.ast_builder.up(savestate_node)

    def _if_else(self, ):
        """if else

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) else ({ <code_ss> }|<s>)
        """
        savestate_node = self.ast_builder.down(IfElse)

        self._if_condition()
        self._branch()

        self.add_and_match([TT.ELSE], NT.Else)
        self._branch()

        self.ast_builder.up(savestate_node)

    def _if_condition(self, ):
        """if code piece

        :grammar: if '('<code_le>')'
        """
        self.match([TT.IF])

        self.match([TT.L_PAREN])

        self.code_le()

        self.match([TT.R_PAREN])

    def _branch(self, ):
        """if code piece

        :grammar: ({ <code_ss> }|<s>)
        """
        if self.LTT(1) == TT.L_BRACE:
            self.consume_next_token()  # [TT.L_BRACE]

            self.code_ss()

            self.match([TT.R_BRACE])
        elif self.LTT(1) in self.STATEMENT:
            self._s()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                TT.L_BRACE.value + " or single statement", token.value,
                token.position)
