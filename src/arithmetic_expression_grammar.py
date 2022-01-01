from parser_ import BacktrackingParser
from arithmetic_nodes import (ArithmeticUnaryOperation,
                              ArithmeticBinaryOperation,
                              ArithmeticOperand)
from errors import MismatchedTokenError
from lexer import TT


class ArithmeticExpressionGrammar(BacktrackingParser):
    """The arithmetic expression part of the context free grammer of the piocC
    language"""

    BINOP_PREC_1 = [TT.MUL_OP, TT.DIV_OP, TT.MOD_OP]
    BINOP_PREC_2 = [TT.PLUS_OP, TT.MINUS_OP, TT.OPLUS_OP, TT.AND_OP, TT.OR_OP]
    #  UNARY_OP = [TT.MINUS_OP, TT.NOT_OP]

    def __init__(self, lexer):
        super().__init__(lexer)

    def code_ae(self):
        """arithmetic expression startpoint

        :grammer: <prec2>
        :returns: None
        """
        self._prec2()

    def _prec2(self):
        """precedence 2

        :grammer: #2 <prec1> ((<binop_prec2>|<minus>) #2 <prec1>)*
        :returns: None
        """
        savestate_node = self.ast_builder.down(ArithmeticBinaryOperation)

        self._prec1()

        while self.LTT(1) in self.BINOP_PREC_2:
            self.match_and_determine(self.BINOP_PREC_2)

            self.ast_builder.down(ArithmeticBinaryOperation)

            self._prec1()

        self.ast_builder.up(savestate_node)

    def _prec1(self):
        """precedence 1

        :grammer:  #2 <ao> (<binop_prec1> #2 <ao>)*
        :returns: None
        """
        savestate_node = self.ast_builder.down(ArithmeticBinaryOperation)

        self._ao()

        while self.LTT(1) in self.BINOP_PREC_1:
            self.match_and_determine(self.BINOP_PREC_1)

            self.ast_builder.down(ArithmeticBinaryOperation)

            self._ao()

        self.ast_builder.up(savestate_node)

    def _ao(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        :returns: None
        """
        tt = self.LTT(1)
        match tt:
            case TT.IDENTIFIER:
                self.match_and_add([TT.IDENTIFIER], ArithmeticOperand)
            case TT.NUMBER:
                self.match_and_add([TT.NUMBER], ArithmeticOperand)
            case TT.CHARACTER:
                self.match_and_add([TT.CHARACTER], ArithmeticOperand)
            case TT.L_PAREN:
                self._paren_arith()
            #  case _ if tt in self.UNARY_OP:
            case (TT.NOT_OP | TT.MINUS_OP):
                self._unop()
            case _:
                raise MismatchedTokenError("aritmetic operand", self.LT(1))

    def _paren_arith(self):
        """arithmetic parenthesis

        :grammer: ( <code_ae> )
        :returns: None
        """
        self.match([TT.L_PAREN])
        self.code_ae()
        self.match([TT.R_PAREN])

    def _unop(self):
        """unary operator

        :grammer: #1 (<unop>|<minus> #1)+ <ao>
        :returns: None
        """
        savestate_node = self.ast_builder.down(ArithmeticUnaryOperation)

        while True:
            self.match_and_determine(self.UNARY_OP)
            if self.LTT(1) not in self.UNARY_OP:
                break

            self.ast_builder.down(ArithmeticUnaryOperation)

        self._ao()

        self.ast_builder.up(savestate_node)
