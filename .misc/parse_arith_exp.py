from parser import BacktrackingParser
from errors import Errors
from lexer import TT
from picoc_nodes import N


class ArithExpParser(BacktrackingParser):
    """The arithmetic expression part of the context free grammer of the piocC
    language"""

    BINOP_PREC_1 = {
        TT.MUL: N.Mul,
        TT.DIV: N.Div,
        TT.MOD: N.Mod,
    }
    BINOP_PREC_2 = {
        TT.ADD: N.Add,
        TT.MINUS: N.Sub,
        TT.OPLUS: N.Oplus,
        TT.LOGIC_AND: N.And,
        TT.LOGIC_OR: N.Or,
    }
    UNARY = {TT.LOGIC_NOT: N.Not, TT.MINUS: N.Minus}

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

        savestate_node = self.ast_builder.down(N.BinOp)

        self._prec1()

        if self.LTT(1) not in self.BINOP_PREC_2.keys():
            self.ast_builder.go_back("_prec2")
            return
        else:
            self.ast_builder.discard("_prec2")

        while self.LTT(1) in self.BINOP_PREC_2.keys():
            self.add_and_consume(mapping=self.BINOP_PREC_2)

            self.ast_builder.save("_prec2_loop")

            self.ast_builder.down(N.BinOp)

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

        savestate_node = self.ast_builder.down(N.BinOp)

        self._arith_opd()

        if self.LTT(1) not in self.BINOP_PREC_1.keys():
            self.ast_builder.go_back("_prec1")
            return
        else:
            self.ast_builder.discard("_prec1")

        while self.LTT(1) in self.BINOP_PREC_1.keys():
            self.add_and_consume(mapping=self.BINOP_PREC_1)

            self.ast_builder.save("_prec1_loop")
            self.ast_builder.down(N.BinOp)

            self._arith_opd()

            if self.LTT(1) not in self.BINOP_PREC_1.keys():
                self.ast_builder.go_back("_prec1_loop")
            else:
                self.ast_builder.discard("_prec1_loop")

        self.ast_builder.up(savestate_node)

    def _arith_opd(self):
        """arithmetic operand

        :grammer: <word> | <number> | <paren> | <unop>
        """
        if self.LTT(1) == TT.IDENTIFIER:
            self.add_and_consume(classname=N.Name)
        elif self.LTT(1) == TT.NUMBER:
            self.add_and_consume(classname=N.Num)
        elif self.LTT(1) == TT.CHARACTER:
            self.add_and_consume(classname=N.Char)
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
        savestate_node = self.ast_builder.down(N.UnOp)

        while True:
            self.add_and_consume(mapping=self.UNARY)

            if self.LTT(1) not in self.UNARY.keys():
                break

            self.ast_builder.down(N.UnOp)

        self._arith_opd()

        self.ast_builder.up(savestate_node)
