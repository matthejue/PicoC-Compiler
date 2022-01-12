from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from lexer import TT
from logic_nodes import LogicBinaryOperation, Not, Atom, ToBool
from errors import Errors
from dummy_nodes import NT
from itertools import chain


class LogicExpressionGrammar(ArithmeticExpressionGrammar):
    """The logic expression part of the context free grammar of the piocC
    language"""

    COMP_REL = {
        TT.EQ_COMP: NT.Eq,
        TT.UEQ_COMP: NT.UEq,
        TT.LT_COMP: NT.Lt,
        TT.GT_COMP: NT.Gt,
        TT.LE_COMP: NT.Le,
        TT.GE_COMP: NT.Ge
    }
    # TODO: da stimmt noch was nicht, später löschen
    LOG_CON = {TT.AND: NT.LAnd, TT.OR: NT.LOr}  # TT.NOT: NT.LNot

    def code_ae_le(self):
        """point where it's decided if it's a arithmetic expression only or a
        logic expression

        :grammar: #2 <code_ae> (<comp_op> #2 <code_le>)?
        :returns: None
        """
        # it's important that arithmetic grammar is before logic grammar,
        # because both arithmetic and logic grammar have single numbers. In
        # arithmetic grammar they're just numbers and in logic grammar
        # there're 0 and numbers greater 0
        errors = []
        if self.taste(self._taste_consume_ae, errors):
            self._taste_consume_ae()
        elif self.taste(self.code_le, errors):
            self.code_le()
        else:
            self._handle_all_tastes_unsuccessful(
                "arithmetic or logic expression", errors)

    def _handle_all_tastes_unsuccessful(self, expected, errors):
        # if both threw the same error print that error out
        if errors[0].expected == errors[1].expected:
            raise errors[0]
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError(expected, token.value,
                                               token.position)

    def _taste_consume_ae(self):
        """taste whether the next expression is a arithmetic expression

        :grammar: <code_ae>
        :returns: None
        """
        self.code_ae()
        if self.LTT(1) in chain(self.COMP_REL.keys(), self.LOG_CON.keys()):
            raise Errors.TastingError()

    def code_le(self):
        """logic expression startpoint

        :grammar: <or_expr>
        :returns: None
        """
        self._or_expr()

    def _or_expr(self):
        """or expression

        :grammar: #2 <and_expr> (or #2 <and_expr>)*
        :returns: None
        """
        self.ast_builder.save("_or_expr")

        savestate_node = self.ast_builder.down(LogicBinaryOperation)

        self._and_expr()

        if self.LTT(1) != TT.OR:
            self.ast_builder.go_back("_or_expr")
            return
        else:
            self.ast_builder.discard("_or_expr")

        while self.LTT(1) == TT.OR:
            self.add_and_consume(classname=NT.LOr)

            self.ast_builder.save("_or_expr")

            self.ast_builder.down(LogicBinaryOperation)
            self._and_expr()

            if self.LTT(1) != TT.OR:
                self.ast_builder.go_back("_or_expr")
                return
            else:
                self.ast_builder.discard("_or_expr")

        self.ast_builder.up(savestate_node)

    def _and_expr(self):
        """and expression

        :grammar: #2 <lo> (and #2 <lo>)*
        :returns: None
        """
        self.ast_builder.save("_and_expr")

        savestate_node = self.ast_builder.down(LogicBinaryOperation)

        self._lo()

        if self.LTT(1) != TT.AND:
            self.ast_builder.go_back("_and_expr")
            return
        else:
            self.ast_builder.discard("_and_expr")

        while self.LTT(1) == TT.AND:
            self.add_and_consume(classname=NT.LAnd)

            self.ast_builder.save("_and_expr")

            self.ast_builder.down(LogicBinaryOperation)
            self._lo()

            if self.LTT(1) != TT.AND:
                self.ast_builder.go_back("_and_expr")
                return
            else:
                self.ast_builder.discard("_and_expr")

        self.ast_builder.up(savestate_node)

    def _lo(self):
        """logic operand

        :grammar: <not_expr>
        :returns: None
        """
        if self.LTT(1) == TT.NOT:
            self._not_expr()
        elif self.LTT(1) in [TT.NUMBER, TT.CHARACTER, TT.NAME, TT.L_PAREN]:
            self._parenthized_logic_expression_or_arithmetic_term_or_comparison(
            )
        else:
            token = self.LT(1)
            raise Errors.NoApplicableRuleError("logic operand", token.value,
                                               token.position)

    def _not_expr(self):
        """not expression

        :grammar: !+ <code_le>
        :returns: None
        """
        savestate_node = self.ast_builder.down(Not)

        while True:
            self.consume_next_token()  # NT.LNot

            if self.LTT(1) != TT.NOT:
                break

            self.ast_builder.down(Not)

        self._lo()

        self.ast_builder.up(savestate_node)

    def _parenthized_logic_expression_or_arithmetic_term_or_comparison(self):
        """atomic formula or top / bottom

        :grammar: #1 <code_ae> | (#2 <code_ae> <comp_op> <code_ae>)
        :returns: None
        """
        errors = []
        if self.taste(self._taste_consume_parenthesized_logic_expression,
                      errors):
            self._taste_consume_parenthesized_logic_expression()
        elif self.taste(self._taste_consume_arithmetic_term, errors):
            self._taste_consume_arithmetic_term()
        elif self.taste(self._atom, errors):
            self._atom()
        else:
            self._handle_all_tastes_unsuccessful(
                "parenthized logic formula or arithmetic term or comparison",
                errors)

    def _taste_consume_parenthesized_logic_expression(self, ):
        self._taste_consume_parenthesized_logic_expression()
        if self.LTT(1) in chain(self.BINOP_PREC_2, self.BINOP_PREC_1,
                                self.COMP_REL.keys()):
            raise Errors.TastingError()

    def _parenthesized_logic_expression(self):
        """logic parenthesis

        :grammar: ( <code_le> )
        :returns: None
        """
        self.consume_next_token()  # [TT.L_PAREN]
        self.code_le()
        self.match([TT.R_PAREN])

    def _taste_consume_arithmetic_term(self, ):
        __import__('pudb').set_trace()
        self._arithmetic_term()
        # don't allow it to be a atom
        if self.LTT(1) in self.COMP_REL.keys():
            raise Errors.TastingError()

    def _arithmetic_term(self, ):
        """top / bottom

        :grammar: #1 <code_ae>
        :returns: None
        """
        savestate_node = self.ast_builder.down(ToBool)

        self.code_ae()

        self.ast_builder.up(savestate_node)

    def _atom(self, ):
        """atomic formula

        :grammar: #2 <code_ae> <comp_op> <code_ae>
        :returns: None
        """
        savestate_node = self.ast_builder.down(Atom)

        self.code_ae()
        self.add_and_match(list(self.COMP_REL.keys()), mapping=self.COMP_REL)
        self.code_ae()

        self.ast_builder.up(savestate_node)
