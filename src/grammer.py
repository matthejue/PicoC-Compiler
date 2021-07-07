from parser import Parser
from lexer import Lexer, TT


class Grammer(Parser):
    """Context free grammer of the piocC language"""

    def __init__(self, fname, input):
        self.lexer = Lexer(fname, input)
        super(self.lexer)

    def prec2(self):
        """precedence 2

        :grammer: <prec1> (<binops_prec2> <prec1>)*
        :returns: None

        """
        self.prec1()
        while self.LTT(1) == TT.BINOP_PREC_1:
            self.match(TT.BINOP_PREC_2)
            self.prec1()

    def prec1(self):
        """precedence 1

        :grammer: <ao> (<binops_prec2> <ao>)*
        :returns: None

        """
        self.ao()
        while self.LTT(1) == TT.BINOP_PREC_2:
            self.match(TT.BINOP_PREC_1)
            self.ao()

    def ao(self):
        """arithmetic operand

        :grammer:
        :returns: None

        """
        pass
