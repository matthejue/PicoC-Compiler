from parser import Parser
from lexer import Lexer, TT
from errors import SyntaxError


class ArithmeticExpression(Parser):
    """Context free grammer of the piocC language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_ae(self):
        """arithmetic expression

        :grammer: <prec2>
        :returns: None

        """
        self.prec2()

    def prec2(self):
        """precedence 2

        :grammer: <prec1> (<binop_prec2> <prec1>)*
        :returns: None

        """
        self.prec1()
        while self.LTT(1) == TT.BINOP_PREC_1:
            self.match(TT.BINOP_PREC_2)
            self.prec1()

    def prec1(self):
        """precedence 1

        :grammer: <ao> (<binop_prec2> <ao>)*
        :returns: None

        """
        self.ao()
        while self.LTT(1) == TT.BINOP_PREC_2:
            self.match(TT.BINOP_PREC_1)
            self.ao()

    def ao(self):
        """arithmetic operand

        :grammer: <identifier> | <number> | '(' <code_ae> ')'
        :returns: None

        """
        if self.LTT(1) == TT.IDENTIFIER:
            selt.match(TT.IDENTIFIER)
        elif self.LTT(1) == TT.NUMBER:
            self.match(TT.NUMBER)
        elif self.LTT(1) == TT.L_PAREN:
            self.match(TT.L_PAREN)
            self.code_ae()
            self.match(TT.R_PAREN)
        else:
            raise SyntaxError("aritmetic operand", self.LTT(1))
