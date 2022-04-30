from parse_arith_exp import ArithExpParser
from lexer import TT
from errors import Errors
from picoc_nodes import N
from itertools import chain
from reference import Reference


class LogicExpParser(ArithExpParser):
    """The logic expression part of the context free grammar of the piocC
    language"""

    COMP_REL = {
        TT.EQ: N.Eq,
        TT.NEQ: N.NEq,
        TT.LT: N.Lt,
        TT.GT: N.Gt,
        TT.LTE: N.LtE,
        TT.GTE: N.GtE,
    }
    LOG_CON = {TT.LOGIC_AND: N.LogicAnd, TT.LOGIC_OR: N.LogicOr}  # TT.NOT: NT.LNot

    def parse_arith_exp_logic_exp(self):
        """point where it's decided if it's a arithmetic expression only or a
        logic expression

        :grammar: #2 <code_ae> (<comp_op> #2 <code_le>)?
        """
        # it's important that arithmetic grammar is before logic grammar,
        # because both arithmetic and logic grammar have single numbers. In
        # arithmetic grammar they're just numbers and in logic grammar
        # there're 0 and numbers greater 0
        error = Reference()
        if self.taste(self._taste_arith_exp, error):
            self._taste_arith_exp()
        elif self.taste(self.parse_logic_exp, error):
            self.parse_logic_exp()
        else:
            raise error.val
            #  self._handle_all_tastes_unsuccessful(
            #  "arithmetic or logic expression", error)

    def _taste_arith_exp(self):
        """taste whether the next expression is a arithmetic expression

        :grammar: <code_ae>
        """
        self.parse_arithm_exp()
        if self.LTT(1) in chain(self.COMP_REL.keys(), self.LOG_CON.keys()):
            raise Errors.TastingError()

    def parse_logic_exp(self):
        """logic expression startpoint

        :grammar: <or_expr>
        """
        self._or_exp()

    def _or_exp(self):
        """or expression

        :grammar: #2 <and_expr> (or #2 <and_expr>)*
        """
        self.ast_builder.save("_or_expr")

        savestate_node = self.ast_builder.down(N.LogicBinOp)

        self._and_exp()

        if self.LTT(1) != TT.LOGIC_OR:
            self.ast_builder.go_back("_or_expr")
            return
        else:
            self.ast_builder.discard("_or_expr")

        while self.LTT(1) == TT.LOGIC_OR:
            self.add_and_consume(classname=N.LogicOr)

            self.ast_builder.save("_or_expr")

            self.ast_builder.down(N.LogicBinOp)
            self._and_exp()

            if self.LTT(1) != TT.LOGIC_OR:
                self.ast_builder.go_back("_or_expr")
            else:
                self.ast_builder.discard("_or_expr")

        self.ast_builder.up(savestate_node)

    def _and_exp(self):
        """and expression

        :grammar: #2 <lo> (and #2 <lo>)*
        """
        self.ast_builder.save("_and_expr")

        savestate_node = self.ast_builder.down(N.LogicBinOp)

        self._logic_opd()

        if self.LTT(1) != TT.LOGIC_AND:
            self.ast_builder.go_back("_and_expr")
            return
        else:
            self.ast_builder.discard("_and_expr")

        while self.LTT(1) == TT.LOGIC_AND:
            self.add_and_consume(classname=N.LogicAnd)

            self.ast_builder.save("_and_expr")

            self.ast_builder.down(N.LogicBinOp)
            self._logic_opd()

            if self.LTT(1) != TT.LOGIC_AND:
                self.ast_builder.go_back("_and_expr")
            else:
                self.ast_builder.discard("_and_expr")

        self.ast_builder.up(savestate_node)

    def _logic_opd(self):
        """logic operand

        :grammar: <not_expr>
        """
        if self.LTT(1) == TT.LOGIC_NOT:
            self._not_exp()
        elif self.LTT(1) in [
            TT.NUMBER,
            TT.CHARACTER,
            TT.IDENTIFIER,
            TT.L_PAREN,
            TT.MINUS,
        ]:
            self._paren_logic_exp_arith_exp_atom()
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(
                "logic operand", token.value, token.position
            )

    def _not_exp(self):
        """not expression

        :grammar: !+ <code_le>
        """
        savestate_node = self.ast_builder.down(N.LogicNot)

        while True:
            self.consume_next_token()  # NT.LNot

            if self.LTT(1) != TT.LOGIC_NOT:
                break

            self.ast_builder.down(N.LogicNot)

        self._logic_opd()

        self.ast_builder.up(savestate_node)

    def _paren_logic_exp_arith_exp_atom(self):
        """atomic formula or top / bottom

        :grammar: #1 <code_ae> | (#2 <code_ae> <comp_op> <code_ae>)
        """
        error = Reference()
        if self.taste(self._taste_paren_logic_exp, error):
            self._taste_paren_logic_exp()
        elif self.taste(self._taste_arith_exp_as_logic_atom, error):
            self._taste_arith_exp_as_logic_atom()
        elif self.taste(self._atom, error):
            self._atom()
        else:
            raise error.val
            #  self._handle_all_tastes_unsuccessful(
            #  "parenthized logic formula or arithmetic term or comparison",
            #  errors)

    def _taste_paren_logic_exp(self):
        self._paren_logic_exp()
        if self.LTT(1) in chain(
            self.BINOP_PREC_2, self.BINOP_PREC_1, self.COMP_REL.keys()
        ):
            raise Errors.TastingError()

    def _paren_logic_exp(self):
        """logic parenthesis

        :grammar: ( <code_le> )
        """
        self.match([TT.L_PAREN])
        self.parse_logic_exp()
        self.match([TT.R_PAREN])

    def _taste_arith_exp_as_logic_atom(self):
        self._arith_exp_as_logic_atom()
        # don't allow it to be a atom
        if self.LTT(1) in self.COMP_REL.keys():
            raise Errors.TastingError()

    def _arith_exp_as_logic_atom(self):
        """top / bottom

        :grammar: #1 <code_ae>
        """
        savestate_node = self.ast_builder.down(N.ToBool)

        self.parse_arithm_exp()

        self.ast_builder.up(savestate_node)

    def _atom(self):
        """atomic formula

        :grammar: #2 <code_ae> <comp_op> <code_ae>
        """
        savestate_node = self.ast_builder.down(N.Atom)

        self.parse_arithm_exp()
        self.add_and_match(list(self.COMP_REL.keys()), mapping=self.COMP_REL)
        self.parse_arithm_exp()

        self.ast_builder.up(savestate_node)
