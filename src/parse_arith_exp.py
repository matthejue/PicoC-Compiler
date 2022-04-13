from parser import BacktrackingParser
from errors import Errors
from lexer import TT
from picoc_nodes import NT


class ArithExpParser(BacktrackingParser):
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
    UNARY = {TT.NEG_OP: NT.Not, TT.MINUS_OP: NT.Minus}

    def parse_arithm_exp(self):
        """arithmetic expression startpoint

        :grammer: <prec2>
        """
        self._prec2()

    def _prec2(self):
        """precedence 2

        :grammer: #2 <prec1> ((<binop_prec2>|<minus>) #2 <prec1>)*
        """
        self.ast_builder.save("_prec2")

        savestate_node = self.ast_builder.down(NT.ArithBinOp)

        self._prec1()

        if self.LTT(1) not in self.BINOP_PREC_2.keys():
            self.ast_builder.go_back("_prec2")
            return
        else:
            self.ast_builder.discard("_prec2")

        while self.LTT(1) in self.BINOP_PREC_2.keys():
            self.add_and_consume(mapping=self.BINOP_PREC_2)

            self.ast_builder.save("_prec2_loop")

            self.ast_builder.down(NT.ArithBinOp)

            self._prec1()

            if self.LTT(1) not in self.BINOP_PREC_2.keys():
                self.ast_builder.go_back("_prec2_loop")
            else:
                self.ast_builder.discard("_prec2_loop")

        self.ast_builder.up(savestate_node)

    def _prec1(self):
        """precedence 1

        :grammer: #2 <ao> (<binop_prec1> #2 <ao>)*
        """
        self.ast_builder.save("_prec1")

        savestate_node = self.ast_builder.down(NT.ArithBinOp)

        self._arith_op()

        if self.LTT(1) not in self.BINOP_PREC_1.keys():
            self.ast_builder.go_back("_prec1")
            return
        else:
            self.ast_builder.discard("_prec1")

        while self.LTT(1) in self.BINOP_PREC_1.keys():
            self.add_and_consume(mapping=self.BINOP_PREC_1)

            self.ast_builder.save("_prec1_loop")
            self.ast_builder.down(NT.ArithBinOp)

            self._arith_op()

            if self.LTT(1) not in self.BINOP_PREC_1.keys():
                self.ast_builder.go_back("_prec1_loop")
            else:
                self.ast_builder.discard("_prec1_loop")

        self.ast_builder.up(savestate_node)

    def _arith_op(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        """
        if self.LTT(1) == TT.IDENTIFIER:
            self.add_and_consume(classname=NT.Name)
        elif self.LTT(1) == TT.NUMBER:
            self.add_and_consume(classname=NT.Num)
        elif self.LTT(1) == TT.CHARACTER:
            self.add_and_consume(classname=NT.Char)
        elif self.LTT(1) == TT.L_PAREN:
            self._paren_arith()
        elif self.LTT(1) in self.UNARY.keys():
            self._unary_op()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                "arithmetic operand", token.value, token.position
            )

    def _paren_arith(self):
        """arithmetic parenthesis

        :grammer: ( <code_ae> )
        """
        self.match([TT.L_PAREN])
        self.parse_arith_logic_exp()
        self.match([TT.R_PAREN])

    def _unary_op(self):
        """unary operator

        :grammer: #1 (<unop>|<minus> #1)+ <ao>
        """
        savestate_node = self.ast_builder.down(NT.ArithUnaryOp)

        while True:
            self.add_and_consume(mapping=self.UNARY)

            if self.LTT(1) not in self.UNARY.keys():
                break

            self.ast_builder.down(NT.ArithUnaryOp)

        self._arith_op()

        self.ast_builder.up(savestate_node)
