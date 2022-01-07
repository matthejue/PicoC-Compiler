from logic_expression_grammar import LogicExpressionGrammar
from assignment_allocation_nodes import Assign, Alloc
from lexer import TT
from dummy_nodes import NT
from errors import MismatchedTokenError
from itertools import chain


class AssignmentAllocationGrammar(LogicExpressionGrammar):
    """The assignment expression part of the context free grammar of the piocC
    language"""

    PRIM_DT = {TT.INT: NT.Int, TT.CHAR: NT.Char, TT.VOID: NT.Void}

    def code_aa(self):
        """assignment and allocation startpoint

        :grammar: <aa>
        """
        self._aa()

    def _aa(self):
        """assignment and allocation

        :grammar: #2 (<identifier> | <alloc>) (= #2 (<identifier> = #2) * <ae_le>)?
        """
        savestate_node = self.ast_builder.down(Assign)

        if self.LTT(1) in chain(self.PRIM_DT.keys(), [TT.CONST]):
            self._alloc()
        elif self.LTT(1) == TT.IDENTIFIER:
            self.add(classname=NT.Identifier)
            self._assign()
        else:
            raise MismatchedTokenError("identifier or allocation", self.LT(1))

        self.ast_builder.up(savestate_node)

    def _assign(self, ):
        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            self.ast_builder.down(Assign)

            while self.LTT(2) == TT.ASSIGNMENT:
                self.match_and_add([TT.IDENTIFIER], classname=NT.Identifier)
                self.consume_next_token()  # [TT.ASSIGNMENT]

                self.ast_builder.down(Assign)

            self.code_ae_le()
        else:
            raise MismatchedTokenError("assignment", self.LT(1))

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <const>? <prim_dt> <identifier>
        """
        savestate_node = self.ast_builder.down(Alloc)

        if self.LTT(1) == TT.CONST:
            self.add(classname=NT.Const)

        self.match_and_add(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)
        self.match_and_add([TT.IDENTIFIER], classname=NT.Identifier)

        self.ast_builder.up(savestate_node)

        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            self.ast_builder.down(Assign)

            while self.LTT(1) == TT.IDENTIFIER:
                self.add(classname=NT.Identifier)
                self.match([TT.ASSIGNMENT])

                self.ast_builder.down(Assign)

            self.code_ae_le()
