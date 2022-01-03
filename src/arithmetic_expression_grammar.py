from parser_ import BacktrackingParser
from arithmetic_nodes import (ArithUnOp, ArithBinOp, Identifier, Number,
                              Character)
from errors import MismatchedTokenError
from lexer import TT
from dummy_nodes import Add, Sub, Mul, Div, Mod, Oplus, Or, And, Minus, Not


class ArithmeticExpressionGrammar(BacktrackingParser):
    """The arithmetic expression part of the context free grammer of the piocC
    language"""

    BINOP_PREC_1 = {TT.MUL_OP: Mul, TT.DIV_OP: Div, TT.MOD_OP: Mod}
    BINOP_PREC_2 = {
        TT.PLUS_OP: Add,
        TT.MINUS_OP: Sub,
        TT.OPLUS_OP: Oplus,
        TT.AND_OP: And,
        TT.OR_OP: Or
    }
    UNARY_OP = {TT.MINUS_OP: Minus, TT.NOT_OP: Not}

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
        savestate_node = self.ast_builder.down(ArithBinOp)

        self._prec1()

        while self.LTT(1) in self.BINOP_PREC_2.keys():
            self.choose(self.BINOP_PREC_2)
            self.no_ignore()
            self.ast_builder.down(ArithBinOp)

            self._prec1()

        self.ast_builder.up(savestate_node)

    def _prec1(self):
        """precedence 1

        :grammer:  #2 <ao> (<binop_prec1> #2 <ao>)*
        :returns: None
        """
        savestate_node = self.ast_builder.down(ArithBinOp)

        self._ao()

        while self.LTT(1) in self.BINOP_PREC_1.keys():
            self.choose(self.BINOP_PREC_1)
            self.no_ignore()
            self.ast_builder.down(ArithBinOp)

            self._ao()

        self.ast_builder.up(savestate_node)

    def _ao(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        :returns: None
        """
        if self.LTT(1) == TT.IDENTIFIER:
            self.match_and_add([TT.IDENTIFIER], Identifier)
        elif self.LTT(1) == TT.NUMBER:
            self.match_and_add([TT.NUMBER], Number)
        elif self.LTT(1) == TT.CHARACTER:
            self.match_and_add([TT.CHARACTER], Character)
        elif self.LTT(1) == TT.L_PAREN:
            self._paren_arith()
        elif self.LTT(1) in self.UNARY_OP:
            self._unop()
        else:
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
        savestate_node = self.ast_builder.down(ArithUnOp)

        while True:
            self.match_and_choose(self.UNARY_OP)
            self.no_ignore()
            if self.LTT(1) not in self.UNARY_OP.keys():
                break

            self.ast_builder.down(ArithUnOp)

        self._ao()

        self.ast_builder.up(savestate_node)
