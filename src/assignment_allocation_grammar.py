from logic_expression_grammar import LogicExpressionGrammar
from assignment_allocation_nodes import Assign, Alloc
from arithmetic_nodes import Identifier
from lexer import TT
from dummy_nodes import NT
from errors import Errors


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

        if self.LTT(1) in self.PRIM_DT.keys():
            self._alloc()
        elif self.LTT(1) == TT.CONST:
            self.ast_builder.discard("_aa")
            self._constant_assign()
        elif self.LTT(1) == TT.NAME:
            self.ast_builder.discard("_aa")
            self.add_and_consume(classname=Identifier)
            self._assign()
        else:
            token = self.LT(1)
            raise Errors.MismatchedTokenError(
                "identifier or start of a allocation", token.value,
                token.position)

        self.ast_builder.up(savestate_node)

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <const>? <prim_dt> <identifier>
        """
        savestate_node = self.ast_builder.down(Alloc)

        self.add_and_match(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)
        self.add_and_match([TT.NAME], classname=Identifier)

        self.ast_builder.up(savestate_node)

        if self.LTT(1) != TT.ASSIGNMENT:
            self.ast_builder.go_back("_aa")
        else:
            self.ast_builder.discard("_aa")

        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            while self.LTT(2) == TT.ASSIGNMENT:
                self.ast_builder.down(Assign)
                self.add_and_match([TT.NAME], classname=Identifier)
                self.consume_next_token()  # [TT.ASSIGNMENT]

            self.code_ae_le()

    def _constant_assign(self, ):
        savestate_node = self.ast_builder.down(Alloc)

        self.add_and_consume(classname=NT.Const)

        self.add_and_match(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)

        self.add_and_match([TT.NAME], classname=Identifier)

        self.ast_builder.up(savestate_node)

        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            self.code_ae_le()
        else:
            token = self.LT(1)
            raise Errors.MismatchedTokenError("assignment operator",
                                              token.value, token.position)

    def _assign(self, ):
        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            while self.LTT(2) == TT.ASSIGNMENT:
                self.ast_builder.down(Assign)
                self.add_and_match([TT.NAME], classname=Identifier)
                self.consume_next_token()  # [TT.ASSIGNMENT]

            self.code_ae_le()
        else:
            token = self.LT(1)
            raise Errors.MismatchedTokenError("assignment operator",
                                              token.value, token.position)
