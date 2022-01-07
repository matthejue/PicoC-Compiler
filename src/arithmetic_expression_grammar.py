from parser_ import BacktrackingParser
from arithmetic_nodes import (ArithUnOp, ArithBinOp)
from errors import MismatchedTokenError
from lexer import TT
from dummy_nodes import NT


class ArithmeticExpressionGrammar(BacktrackingParser):
    """The arithmetic expression part of the context free grammer of the piocC
    language"""

    BINOP_PREC_1 = {
        TT.MUL_OP: NT.Mul,
        TT.DIV_OP: NT.Div,
        TT.MOD_OP: NT.Mod,
    }
    BINOP_PREC_2 = {
        TT.PLUS_OP: NT.Add,
        TT.MINUS_OP: NT.Sub,
        TT.OPLUS_OP: NT.Oplus,
        TT.AND_OP: NT.And,
        TT.OR_OP: NT.Or,
    }
    UNARY = {TT.NOT_OP: NT.Not, TT.MINUS_OP: NT.Minus}

    def code_ae(self):
        """arithmetic expression startpoint

        :grammer: <prec2>
        """
        self._prec2()

    def _prec2(self):
        """precedence 2

        :grammer: #2 <prec1> ((<binop_prec2>|<minus>) #2 <prec1>)*
        """
        if self.LTT(2) not in self.BINOP_PREC_2.keys():
            self._prec1()
            return

        savestate_node = self.ast_builder.down(ArithBinOp)

        self._prec1()

        while self.LTT(1) in self.BINOP_PREC_2.keys():
            self.add(mapping=self.BINOP_PREC_2)
            self.ast_builder.down(ArithBinOp)

            self._prec1()

        self.ast_builder.up(savestate_node)

    def _prec1(self):
        """precedence 1

        :grammer:  #2 <ao> (<binop_prec1> #2 <ao>)*
        """
        if self.LTT(2) not in self.BINOP_PREC_1.keys():
            self._ao()
            return

        savestate_node = self.ast_builder.down(ArithBinOp)

        self._ao()

        while self.LTT(1) in self.BINOP_PREC_1.keys():
            self.add(mapping=self.BINOP_PREC_1)
            self.ast_builder.down(ArithBinOp)

            self._ao()

        self.ast_builder.up(savestate_node)

    def _ao(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        """
        if self.LTT(1) == TT.IDENTIFIER:
            self.add(classname=NT.Identifier)
        elif self.LTT(1) == TT.NUMBER:
            self.add(classname=NT.Number)
        elif self.LTT(1) == TT.CHARACTER:
            self.add(classname=NT.Character)
        elif self.LTT(1) == TT.L_PAREN:
            self._paren_arith()
        elif self.LTT(1) in self.UNARY.keys():
            self._unop()
        else:
            raise MismatchedTokenError("aritmetic operand", self.LT(1))

    def _paren_arith(self):
        """arithmetic parenthesis

        :grammer: ( <code_ae> )
        """
        self.match([TT.L_PAREN])
        self.code_ae()
        self.match([TT.R_PAREN])

    def _unop(self):
        """unary operator

        :grammer: #1 (<unop>|<minus> #1)+ <ao>
        """
        savestate_node = self.ast_builder.down(ArithUnOp)

        while True:
            self.add(mapping=self.UNARY)
            if self.LTT(1) not in self.UNARY.keys():
                break

            self.ast_builder.down(ArithUnOp)

        self._ao()

        self.ast_builder.up(savestate_node)
