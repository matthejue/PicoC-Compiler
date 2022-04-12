from lexer import TT
from errors import Errors
from if_else_nodes import If, IfElse
from picoc_nodes import NT
from reference import Reference


class IfElseParser:
    def parse_if_else(self):
        self._if_if_else()

    def _if_if_else(self):
        """if or if else

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) (else ({
        <code_ss> }|<s>))?
        """
        error = Reference()
        if self.taste(self._taste_if_without_else, error):
            self._taste_if_without_else()
        elif self.taste(self._if_else, error):
            self._if_else()
        else:
            raise error.val

    def _taste_if_without_else(self):
        """taste whether the next expression is a if without else

        :grammar: <if_without_else>
        """
        self._if_without_else()
        if self.LTT(1) == TT.ELSE:
            raise Errors.TastingError()

    def _if_without_else(self):
        """if

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>)
        """
        savestate_node = self.ast_builder.down(If)

        self._condition()
        self._branch()

        self.ast_builder.up(savestate_node)

    def _if_else(self):
        """if else

        :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) else ({ <code_ss> }|<s>)
        """
        savestate_node = self.ast_builder.down(IfElse)

        self._condition()
        self._branch()

        self.add_and_match([TT.ELSE], NT.Else)
        self._branch()

        self.ast_builder.up(savestate_node)

    def _condition(self):
        """if code piece

        :grammar: if '('<code_le>')'
        """
        self.match([TT.IF])

        self.match([TT.L_PAREN])

        self.parse_logic_exp()

        self.match([TT.R_PAREN])

    def _branch(self):
        """if code piece

        :grammar: ({ <code_ss> }|<s>)
        """
        if self.LTT(1) == TT.L_BRACE:
            self.consume_next_token()  # [TT.L_BRACE]

            self.parse_stmts()

            self.match([TT.R_BRACE])
        elif self.LTT(1) in self.STATEMENT:
            self._stmt()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                TT.L_BRACE.value + " or single statement", token.value, token.position
            )
