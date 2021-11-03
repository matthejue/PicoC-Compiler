from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from lexer import TT, Token
from logic_nodes import LogicAndOrNode, LogicNotNode, LogicAtomNode,\
    LogicTopBottomNode
from abstract_syntax_tree import TokenNode
from errors import MismatchedTokenError, NoApplicableRuleError
import global_vars


class LogicExpressionGrammar(ArithmeticExpressionGrammar):

    """The logic expression part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        # super().__init__(lexer, num_lts)
        super().__init__(lexer)

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
            self._handle_all_tastes_unsuccessful("arithmetic expression or "
                                                 "logic expression", errors)

    def _handle_all_tastes_unsuccessful(self, expected, errors):
        # if both threw the same error print that error out
        if errors[0].expected == errors[1].expected:
            raise errors[0]
        # if both threw different errors raise a undefinied
        # NoApplicableRuleError
        else:
            raise NoApplicableRuleError(expected, self.LT(1))

    def _taste_consume_ae(self):
        """taste whether the next expression is a arithmetic expression

        :function: <code_ae> ;
        :returns: None
        """
        self.code_ae()
        if self.LTT(1) == TT.COMP_OP or self._is_logical_connective():
            raise MismatchedTokenError("all besides comparison operators and "
                                       "logical connectives", self.LT(1))

    def _is_logical_connective(self, ):
        return self.LTT(1) == TT.AND or self.LTT(1) == TT.OR or self.LTT(1)\
            == TT.NOT

#     def _taste_consume_le(self):
#         """taste whether the next expression is a logic expression
#
#         :grammar: <code_le> ;
#         :returns: None
#         """
#         self.code_le()
#         self.match([TT.SEMICOLON])

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
        savestate_node = self.ast_builder.down(LogicAndOrNode, [TT.OR])

        self._and_expr()
        while self.LTT(1) == TT.OR:
            self.match_and_add([TT.OR])

            self.ast_builder.down(LogicAndOrNode, [TT.OR])

            self._and_expr()

        self.ast_builder.up(savestate_node)

    def _and_expr(self):
        """and expression

        :grammar: #2 <lo> (and #2 <lo>)*
        :returns: None
        """
        savestate_node = self.ast_builder.down(LogicAndOrNode, [TT.AND])

        self._lo()
        while self.LTT(1) == TT.AND:
            self.match_and_add([TT.AND])

            self.ast_builder.down(LogicAndOrNode, [TT.AND])

            self._lo()

        self.ast_builder.up(savestate_node)

    def _lo(self):
        """logic operand

        :grammar: <not_expr>
        :returns: None
        """
        if self.LTT(1) == TT.NOT:
            self._not_expr()
        elif self.LTT(1) == TT.L_PAREN:
            self._paren_logic()
        elif self.LTT(1) in [TT.NUMBER, TT.IDENTIFIER]:
            self._atom_or_top_bottom()
        else:
            raise MismatchedTokenError("logic operand", self.LT(1))

    def _atom_or_top_bottom(self):
        """atomic formula or top / bottom

        :grammar: #1 <code_ae> | (#2 <code_ae> <comp_op> <code_ae>)
        :returns: None
        """
        errors = []
        if self.taste(self._taste_consume_top_bottom, errors):
            self._taste_consume_top_bottom()
        elif self.taste(self._atom, errors):
            self._atom()
        else:
            self._handle_all_tastes_unsuccessful("logic atom or term", errors)

    def _taste_consume_top_bottom(self, ):
        self._top_bottom()
        # don't allow it to be a atom
        if self.LTT(1) == TT.COMP_OP:
            raise MismatchedTokenError("all besides comparison operators",
                                       self.LT(1))

    def _top_bottom(self, ):
        """top / bottom

        :grammar: #1 <code_ae>
        :returns: None
        """
        savestate_node = self.ast_builder.down(
            LogicTopBottomNode, [TT.TO_BOOL])

        # TODO: little hack to to also have a token for bottomnode
        if not global_vars.is_tasting:
            self.ast_builder.addChild(
                TokenNode(Token(TT.TO_BOOL, "to bool", None)))

        self.code_ae()

        self.ast_builder.up(savestate_node)

    def _atom(self, ):
        """atomic formula

        :grammar: #2 <code_ae> <comp_op> <code_ae>
        :returns: None
        """
        savestate_node = self.ast_builder.down(LogicAtomNode, [TT.COMP_OP])

        self.code_ae()
        self.match_and_add([TT.COMP_OP])
        self.code_ae()

        self.ast_builder.up(savestate_node)

    def _paren_logic(self):
        """logic parenthesis

        :grammar: ( <code_le> )
        :returns: None
        """
        self.match([TT.L_PAREN])
        self.code_le()
        self.match([TT.R_PAREN])

    def _not_expr(self):
        """not expression

        :grammar: !+ <code_le>
        :returns: None
        """
        savestate_node = self.ast_builder.down(LogicNotNode, [TT.NOT])

        while True:
            self.match_and_add(TT.NOT)

            if self.LTT(1) != TT.NOT:
                break

            self.ast_builder.down(LogicNotNode, [TT.NOT])

        self._lo()

        self.ast_builder.up(savestate_node)
