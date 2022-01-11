from assignment_allocation_grammar import AssignmentAllocationGrammar
# from abstract_syntax_tree import ASTNode
from lexer import TT
from errors import Errors
from itertools import chain
from if_else_grammar import IfElseGrammar
from loop_grammar import LoopGrammar


class StatementGrammar(AssignmentAllocationGrammar, IfElseGrammar,
                       LoopGrammar):
    """The statement sequence part of the context free grammar of the piocC
    language"""

    ASSIGNMENT_ALLOCATION = list(
        AssignmentAllocationGrammar.PRIM_DT.keys()) + [TT.CONST, TT.NAME]
    LOOP = [TT.WHILE, TT.DO]
    STATEMENT = [TT.IF, TT.SEMICOLON] + ASSIGNMENT_ALLOCATION + LOOP

    def code_ss(self):
        """statement sequence startpoint

        :grammar: <ss>
        :returns: None

        """
        self._ss()

    def _ss(self):
        """statement sequence

        :grammar: (<s> ;+)+
        :returns: None

        """
        while True:
            self._s()

            if self.LTT(1) == TT.R_BRACE:
                break

    def _s(self):
        """statement

        :grammar: <code_aa>;+ | <code_ie>;* | <code_lo>;* | ;+
        :returns: None

        """
        if self.LTT(1) in self.ASSIGNMENT_ALLOCATION:
            self.code_aa()
            self._semicolons()
        elif self.LTT(1) == TT.IF:
            self.code_ie()
            self._semicolons_or_none()
        elif self.LTT(1) in self.LOOP:
            self.code_lo()
            self._semicolons_or_none()
        elif self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError("start of a statement",
                                               token.value, token.position)

    def _semicolons(self, ):
        while True:
            self.match([TT.SEMICOLON])
            if self.LTT(1) != TT.SEMICOLON:
                break

    def _semicolons_or_none(self, ):
        while self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()  # [TT.SEMICOLON]
