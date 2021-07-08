from parser import Parser

from abstract_syntax_tree import ASTNode
from errors import SyntaxError
from lexer import TT
from grammer import Grammer


class ArithmeticExpression(ASTBuilder):
    """the arithmetic expression part of the context free grammer of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_ae(self):
        """arithmetic expression

        :grammer: <prec2>
        :returns: None

        """
        self._prec2()

    def _prec2(self):
        """precedence 2

        :grammer: <prec1> ((<binop_prec2>|<minus>) <prec1>)*
        :returns: None

        """
        sn = self.down(TT.BINOP_PREC_2, NC.ArithOpNode, self.LTT(1))
        self._prec1()
        while self.LTT(1) in [TT.BINOP_PREC_2, TT.MINUS]:
            if self.LTT(1) == TT.BINOP_PREC_2:
                self.match(TT.BINOP_PREC_2)
            elif self.LTT(1) == TT.MINUS:
                self.match(TT.MINUS)
            self._prec1()
        self.up(sn)

    def _prec1(self):
        """precedence 1

        :grammer: <ao> (<binop_prec1> <ao>)*
        :returns: None

        """
        self._ao()
        while self.LTT(1) == TT.BINOP_PREC_1:
            self.match(TT.BINOP_PREC_1)
            self._ao()

    def _ao(self):
        """arithmetic operand

        :grammer: <identifier> | <number> | <paren> | <unop>
        :returns: None

        """
        if self.LTT(1) == TT.IDENTIFIER:
            self.match(TT.IDENTIFIER)
        elif self.LTT(1) == TT.NUMBER:
            self.match(TT.NUMBER)
        elif self.LTT(1) == TT.L_PAREN:
            self._paren()
        elif self.LTT(1) in [TT.MINUS, TT.UNOP]:
            self._unop()
        else:
            raise SyntaxError("aritmetic operand", self.LT(1))

    def _paren(self):
        """parenthesis

        :grammer: '(' <code_ae> ')'
        :returns: None

        """
        self.match(TT.L_PAREN)
        self.code_ae()
        self.match(TT.R_PAREN)

    def _unop(self, ):
        """unary operator

        :grammer: (<unop>|<minus>)+ number
        :returns: None

        """
        while True:  # do while loop
            if self.LTT(1) == TT.MINUS:
                self.match(TT.MINUS)
            elif self.LTT(1) == TT.UNOP:
                self.match(TT.UNOP)

            if self.LTT(1) not in [TT.MINUS, TT.UNOP]:
                break
        self.match(TT.NUMBER)
