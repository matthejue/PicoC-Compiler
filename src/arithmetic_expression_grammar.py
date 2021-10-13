from parser_ import BacktrackingParser
from abstract_syntax_tree import (ArithmeticUnaryOperationNode,
                                  ArithmeticBinaryOperationNode,
                                  ArithmeticVariableConstantNode)
from errors import MismatchedTokenError
from lexer import TT


class ArithmeticExpressionGrammar(BacktrackingParser):
    """The arithmetic expression part of the context free grammer of the piocC
    language"""

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
        savestate_node = self.ast_builder.down(
            ArithmeticBinaryOperationNode, [TT.BINOP_PREC_2, TT.MINUS])

        self._prec1()

        while self.LTT(1) in [TT.BINOP_PREC_2, TT.MINUS]:
            self.match_and_add([TT.BINOP_PREC_2, TT.MINUS])

            self.ast_builder.down(ArithmeticBinaryOperationNode, [
                                  TT.BINOP_PREC_2, TT.MINUS])

            self._prec1()

        self.ast_builder.up(savestate_node)

    def _prec1(self):
        """precedence 1

        :grammer:  #2 <ao> (<binop_prec1> #2 <ao>)*
        :returns: None

        """
        savestate_node = self.ast_builder.down(
            ArithmeticBinaryOperationNode, [TT.BINOP_PREC_1])

        self._ao()

        while self.LTT(1) == TT.BINOP_PREC_1:
            self.match_and_add([TT.BINOP_PREC_1])

            self.ast_builder.down(
                ArithmeticBinaryOperationNode, [TT.BINOP_PREC_1])

            self._ao()

        self.ast_builder.up(savestate_node)

    def _ao(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        :returns: None

        """
        if self.LTT(1) == TT.IDENTIFIER:
            self._identifier()
        elif self.LTT(1) == TT.NUMBER:
            self._number()
        elif self.LTT(1) == TT.L_PAREN:
            self._paren_arith()
        elif self.LTT(1) in [TT.MINUS, TT.UNARY_OP]:
            # for overlapping symbols liks e.g. '-' which overlap both with
            # e.g. binary and unary operators, a seperate type (here: TT.MINUS)
            # had  to be made and for unary opeartions one has to check both
            # TT.MINUS and TT.UNOP
            self._unop()
        else:
            raise MismatchedTokenError("aritmetic operand", self.LT(1))

    def _identifier(self, ):
        savestate_node = self.ast_builder.down(
            ArithmeticVariableConstantNode, [TT.IDENTIFIER])

        self.match_and_add([TT.IDENTIFIER])

        self.ast_builder.up(savestate_node)

    def _number(self, ):
        savestate_node = self.ast_builder.down(
            ArithmeticVariableConstantNode, [TT.NUMBER])

        self.match_and_add([TT.NUMBER])

        self.ast_builder.up(savestate_node)

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
        savestate_node = self.ast_builder.down(
            ArithmeticUnaryOperationNode, [TT.UNARY_OP, TT.MINUS])

        while True:  # do while loop
            self.match_and_add([TT.UNARY_OP, TT.MINUS])
            if self.LTT(1) not in [TT.UNARY_OP, TT.MINUS]:
                break

            self.ast_builder.down(ArithmeticUnaryOperationNode, [
                                  TT.UNARY_OP, TT.MINUS])

        # self.match_and_add([TT.NUMBER])
        self._ao()

        self.ast_builder.up(savestate_node)
