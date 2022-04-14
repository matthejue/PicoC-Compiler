from parse_logic_exp import LogicExpParser
from lexer import TT
from picoc_nodes import NT
from errors import Errors


class AssignAllocParser(LogicExpParser):
    """The assignment expression part of the context free grammar of the piocC
    language"""

    PRIM_DT = {TT.INT: NT.IntType, TT.CHAR: NT.CharType, TT.VOID: NT.VoidType}

    def parse_assign_alloc(self):
        """assignment and allocation startpoint

        :grammar: <aa>
        """
        self._assign_alloc()

    def _assign_alloc(self):
        """assignment and allocation

        :grammar: #2 (<identifier> | <alloc>) (= #2 (<identifier> = #2)* <ae_le>)?
        """
        self.ast_builder.save("_aa")

        savestate_node = self.ast_builder.down(NT.Assign)

        if self.LTT(1) in self.PRIM_DT.keys():
            self._alloc()
        elif self.LTT(1) == TT.CONST:
            self._constant_assign()
        elif self.LTT(1) == TT.IDENTIFIER:
            self._assign()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                "allocation and / or assignment", token.value, token.position
            )

        self.ast_builder.up(savestate_node)

    def _alloc(self):
        """allocation of a variable

        :grammar: #2 <const>? <prim_dt> <identifier>
        """
        savestate_node = self.ast_builder.down(NT.Alloc)

        self.add_and_match(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)
        self.add_and_match([TT.IDENTIFIER], classname=NT.Name)

        self.ast_builder.up(savestate_node)

        if self.LTT(1) != TT.ASSIGNMENT:
            self.ast_builder.go_back("_aa")
        else:
            self.ast_builder.discard("_aa")

        if self.LTT(1) == TT.ASSIGNMENT:
            self.consume_next_token()  # [TT.ASSIGNMENT]

            while self.LTT(2) == TT.ASSIGNMENT:
                self.ast_builder.down(NT.Assign)
                self.add_and_match([TT.IDENTIFIER], classname=NT.Name)
                self.consume_next_token()  # [TT.ASSIGNMENT]

            self.parse_arith_or_logic_exp()

    def _constant_assign(self):
        self.ast_builder.discard("_aa")

        savestate_node = self.ast_builder.down(NT.Alloc)

        self.add_and_consume(classname=NT.Const)
        self.add_and_match(list(self.PRIM_DT.keys()), mapping=self.PRIM_DT)
        self.add_and_match([TT.IDENTIFIER], classname=NT.Name)

        self.ast_builder.up(savestate_node)

        self.match([TT.ASSIGNMENT])

        #  if self.LTT(1) == TT.IDENTIFIER:
        #  self.add_and_consume(classname=NT.Name)
        if self.LTT(1) == TT.NUMBER:
            self.add_and_consume(classname=NT.Num)
        elif self.LTT(1) == TT.CHARACTER:
            self.add_and_consume(classname=NT.Char)
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                "number or character", token.value, token.position
            )

    def _assign(self):
        self.ast_builder.discard("_aa")

        self.add_and_consume(classname=NT.Name)
        self.match([TT.ASSIGNMENT])

        while self.LTT(2) == TT.ASSIGNMENT:
            self.ast_builder.down(NT.Assign)
            self.add_and_match([TT.IDENTIFIER], classname=NT.Name)
            self.consume_next_token()  # [TT.ASSIGNMENT]

        self.parse_arith_or_logic_exp()
