from logic_expression_grammar import LogicExpressionGrammar
from abstract_syntax_tree import AssignmentNode, AllocationNode
from lexer import TT


class AssignmentAllocationGrammar(LogicExpressionGrammar):

    """The assignment expression part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def code_aa(self):
        """assignment and allocation startpoint

        :grammar: <aa>
        :returns: None

        """
        self._aa()

    def _aa(self):
        """assignment and allocation

        :grammar: #2 <alloc> | ((<word> | <alloc>) = #2 (<word> = #2) * <le>)
        :returns: None

        """
        savestate_node = self.ast_builder.down(
            AssignmentNode, [TT.STATEMENT, TT.ASSIGNMENT])

        if self.LTT(2) == TT.ASSIGNMENT:
            self.match_and_add([TT.IDENTIFIER])
        # elif self.LTT(3) == TT.ASSIGNMENT:
        elif self.LTT(1) == TT.PRIM_DT and self.LTT(2) == TT.IDENTIFIER:
            self._alloc()
        else:
            raise SyntaxError(
                "identifier or assignment expression", self.LT(2))

        self.match_and_add([TT.ASSIGNMENT])

        self.ast_builder.down(AssignmentNode, [TT.ASSIGNMENT])

        while self.LTT(2) == TT.ASSIGNMENT:
            self.match_and_add([TT.IDENTIFIER])
            self.match_and_add([TT.ASSIGNMENT])

            self.ast_builder.down(AssignmentNode, [TT.ASSIGNMENT])

        # self.code_le()
        self.code_ae_le()

        self.ast_builder.up(savestate_node)

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <word> <word> (= <va>)?
        :returns: None

        """
        savestate_node = self.ast_builder.down(AllocationNode, [TT.ALLOC, TT.PRIM_DT])

        self.match_and_add([TT.PRIM_DT])
        self.match_and_add([TT.IDENTIFIER])

        self.ast_builder.up(savestate_node)
