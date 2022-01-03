from logic_expression_grammar import LogicExpressionGrammar
from assignment_allocation_nodes import Assign, Alloc
from lexer import TT
from errors import MismatchedTokenError
from dummy_nodes import Const, Int, Char, Void, Identifier
from itertools import chain


class AssignmentAllocationGrammar(LogicExpressionGrammar):
    """The assignment expression part of the context free grammar of the piocC
    language"""

    PRIM_DT = {TT.INT: Int, TT.CHAR: Char, TT.VOID: Void}

    def code_aa(self):
        """assignment and allocation startpoint

        :grammar: <aa>
        :returns: None

        """
        self._aa()

    def _aa(self):
        """assignment and allocation

        :grammar: #2 (<identifier> | <alloc>) (= #2 (<identifier> = #2) * <ae_le>)?
        :returns: None

        """
        savestate_node = self.ast_builder.down(Assign)

        if self.LTT(1) in chain(self.PRIM_DT.keys(), [TT.CONST]):
            self._alloc()
        elif self.LTT(2) == TT.ASSIGNMENT:
            self.match_and_add([TT.IDENTIFIER], Identifier)
        else:
            raise MismatchedTokenError("identifier or assignment expression",
                                       self.LT(2))

        if self.LTT(1) == TT.ASSIGNMENT:
            self.match([TT.ASSIGNMENT])
            self.no_ignore()

            self.ast_builder.down(Assign)

            while self.LTT(2) == TT.ASSIGNMENT:
                self.match_and_add([TT.IDENTIFIER], Identifier)
                self.match([TT.ASSIGNMENT])
                self.no_ignore()

                self.ast_builder.down(Assign)

            self.code_ae_le()

        self.ast_builder.up(savestate_node)

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <const>? <prim_dt> <identifier>
        :returns: None

        """
        savestate_node = self.ast_builder.down(Alloc)

        if self.LTT(1) == TT.CONST:
            self.match_and_add([TT.CONST], Const)

        self.match_and_choose(self.PRIM_DT)
        self.match_and_add([TT.IDENTIFIER], Identifier)

        self.ast_builder.up(savestate_node)
