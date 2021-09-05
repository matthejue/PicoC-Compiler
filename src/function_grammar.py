from statement_sequence_grammar import StatementSequenceGrammar
from abstract_syntax_tree import MainFunctionNode
from lexer import TT

# TODO: Grammar irgendwo als oberste Grammar noch einrichten


class FunctionGrammar(StatementSequenceGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def code_f(self):
        """function grammar startpoint

        :grammar: <main_function>
        :returns: None

        """
        self._main_function()

    def _main_function(self, ):
        """main function

        :grammar: void main () { <code_ss> }
        :returns: None
        """
        savestate_node = self.ast_builder.down(
            MainFunctionNode, [TT.FUNCTION, TT.MAIN])

        self.match([TT.PRIM_DT])

        self.match_and_add([TT.MAIN])

        self.match([TT.L_PAREN])

        self.match([TT.R_PAREN])

        self.match([TT.L_BRACE])

        self.code_ss()

        self.match([TT.R_BRACE])

        self.ast_builder.up(savestate_node)
