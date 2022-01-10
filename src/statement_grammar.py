from assignment_allocation_grammar import AssignmentAllocationGrammar
# from abstract_syntax_tree import ASTNode
from lexer import TT
from errors import MismatchedTokenError
from itertools import chain
from if_else_grammar import IfElseGrammar
from loop_grammar import LoopGrammar


class StatementGrammar(AssignmentAllocationGrammar, IfElseGrammar,
                       LoopGrammar):
    """The statement sequence part of the context free grammar of the piocC
    language"""
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
        if self._is_assignment_allocation():
            self.code_aa()
            self._semicolons()
        elif self.LTT(1) == TT.IF:
            self.code_ie()
            self._semicolons_or_none()
        elif self._is_loop():
            self.code_lo()
            self._semicolons_or_none()
        elif self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()
        else:
            raise MismatchedTokenError("statement", self.LT(1))

    def _semicolons(self, ):
        while True:
            self.match([TT.SEMICOLON])
            if self.LTT(1) != TT.SEMICOLON:
                break

    def _semicolons_or_none(self, ):
        while self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()  # [TT.SEMICOLON]

    def _is_statement(self):
        return self._is_assignment_allocation() or self.LTT(1) == TT.IF or\
            self._is_loop() or self.LTT(1) == TT.SEMICOLON

    def _is_assignment_allocation(self):
        """Test whether the next statement is a assignment.

        :returns: boolean

        """
        return self.LTT(1) in chain(self.PRIM_DT.keys(), [TT.CONST]) or\
            self.LTT(1) == TT.NAME
        # return (self.LTT(1) == TT.IDENTIFIER and self.LTT(2) == TT.ASSIGNMENT) or\
        # (self.LTT(1) in self.PRIM_DT.keys() and self.LTT(2) == TT.IDENTIFIER) or\
        # (self.LTT(1) == TT.CONST and self.LTT(2) in self.PRIM_DT.keys() and
        # self.LTT(3) == TT.IDENTIFIER)

    def _is_loop(self, ):
        return self.LTT(1) == TT.WHILE or self.LTT(1) == TT.DO
