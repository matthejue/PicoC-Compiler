from parse_assign_alloc import AssignAllocParser

# from ast_node import ASTNode
from lexer import TT
from errors import Errors
from parse_if_else import IfElseParser
from parse_loop import LoopParser


class StmtParser(AssignAllocParser, IfElseParser, LoopParser):
    """The statement sequence part of the context free grammar of the piocC
    language"""

    ASSIGNMENT_ALLOCATION = list(AssignAllocParser.PRIM_DT.keys()) + [
        TT.CONST,
        TT.IDENTIFIER,
    ]
    LOOP = [TT.WHILE, TT.DO]
    STATEMENT = [TT.IF, TT.SEMICOLON] + ASSIGNMENT_ALLOCATION + LOOP

    def parse_stmts(self):
        self._stmts()

    def _stmts(self):
        """statement sequence

        :grammar: (<s> ;+)+
        :returns: None

        """
        while True:
            if self.LTT(1) == TT.R_BRACE:
                break
            self._stmt()

    def _stmt(self):
        """statement

        :grammar: <code_aa>;+ | <code_ie>;* | <code_lo>;* | ;+
        :returns: None

        """
        if self.LTT(1) in self.ASSIGNMENT_ALLOCATION:
            self.parse_assign_alloc()
            self._semicolons()
        elif self.LTT(1) == TT.IF:
            self.parse_if_else()
            self._semicolons_or_none()
        elif self.LTT(1) in self.LOOP:
            self.parse_loop()
            self._semicolons_or_none()
        elif self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError("statement", token.value, token.position)

    def _semicolons(self):
        while True:
            self.match([TT.SEMICOLON])
            if self.LTT(1) != TT.SEMICOLON:
                break

    def _semicolons_or_none(self):
        while self.LTT(1) == TT.SEMICOLON:
            self.consume_next_token()  # [TT.SEMICOLON]
