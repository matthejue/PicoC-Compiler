from logic_expression_grammar import LogicExpressionGrammar
from assignment_allocation_nodes import Assign, Alloc
from arithmetic_nodes import Identifier
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

        :grammar: #2 (<identifier> | <alloc>) (= #2 (<identifier> = #2)* <ae_le>)?
        """
        self.ast_builder.save("_aa")

        savestate_node = self.ast_builder.down(Assign)

        if self.LTT(1) in chain(self.PRIM_DT.keys(), [TT.CONST]):
            self._alloc()
        elif self.LTT(1) == TT.IDENTIFIER:
            self.add_and_consume(classname=Identifier)
            self._assign()
        else:
            raise MismatchedTokenError("identifier or allocation", self.LT(1))

        self.ast_builder.up(savestate_node)

    def _assign(self, ):
        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            while self.LTT(2) == TT.ASSIGNMENT:
                self.ast_builder.down(Assign)
                self.add_and_match([TT.IDENTIFIER], classname=Identifier)
                self.consume_next_token()  # [TT.ASSIGNMENT]

            self.code_ae_le()
        else:
            raise MismatchedTokenError("assignment", self.LT(1))

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <const>? <prim_dt> <identifier>
        """
        savestate_node = self.ast_builder.down(Alloc)

        if self.LTT(1) == TT.CONST:
            self.add_and_consume(classname=NT.Const)

        self.add_and_match(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)
        self.add_and_match([TT.IDENTIFIER], classname=Identifier)

        self.ast_builder.up(savestate_node)

        if self.LTT(1) != TT.ASSIGNMENT:
            self.ast_builder.go_back("_aa")

        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            while self.LTT(2) == TT.ASSIGNMENT:
                self.ast_builder.down(Assign)
                self.add_and_match([TT.IDENTIFIER], classname=Identifier)
                self.consume_next_token()  # [TT.ASSIGNMENT]

            self.code_ae_le()
