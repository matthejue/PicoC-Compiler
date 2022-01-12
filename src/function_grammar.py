from statement_grammar import StatementGrammar
from function_nodes import MainFunction
from lexer import TT
from dummy_nodes import NT
from errors import Errors


class FunctionGrammar(StatementGrammar):
    """the function part of the context free grammar of the piocC
    language"""
    def code_fu(self):
        """function grammar startpoint

        :grammar: <main_function>
        :returns: None

        """
        self._function()

    def _function(self, ):
        if self.LTT(2) == TT.MAIN:
            self._main_function()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError('main function', token.value,
                                               token.position)

    def _main_function(self, ):
        """main function

        :grammar: void main () { <code_ss> }
        :returns: None
        """
        savestate_node = self.ast_builder.down(MainFunction)

        self.add_and_consume(mapping=self.PRIM_DT)

        self.add_and_match([TT.MAIN], NT.Main)

        self.match([TT.L_PAREN])

        self.match([TT.R_PAREN])

        self.match([TT.L_BRACE])

        self.code_ss()

        self.match([TT.R_BRACE])

        self.ast_builder.up(savestate_node)
