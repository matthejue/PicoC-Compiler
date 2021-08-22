from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from lexer import TT
from abstract_syntax_tree import ASTNode
from errors import SyntaxError, NoApplicableRuleError


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
        # TODO: Don't forget to remove this improvised conditional breakpoint
        if self.taste(self.taste_consume_ae):
            # TODO: Wäre try statt taste nicht ein besserer Begriff?
            self.taste_consume_ae()
        elif self.taste(self.taste_consume_le):
            self.taste_consume_le()
        else:
            raise NoApplicableRuleError("arithmetic expression or logic "
                                        "expression", self.LT(1))

    def taste_consume_ae(self):
        """taste whether the next expression is a arithmetic expression

        :function: <code_ae> ;
        :returns: None
        """
        self.code_ae()
        self.match([TT.SEMICOLON])

    def taste_consume_le(self):
        """taste whether the next expression is a logic expression

        :grammar: <code_le> ;
        :returns: None
        """
        self.code_le()
        self.match([TT.SEMICOLON])

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
        savestate_node = self.ast_builder.down(ASTNode, [TT.OR])

        self._and_expr()
        while self.LTT(1) == TT.OR:
            self.match_and_add([TT.OR])

            self.ast_builder.down(ASTNode, [TT.OR])

            self._and_expr()

        self.ast_builder.up(savestate_node)

    def _and_expr(self):
        """and expression

        :grammar: #2 <lo> (and #2 <lo>)*
        :returns: None
        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.AND])

        self._lo()
        while self.LTT(1) == TT.AND:
            self.match_and_add([TT.AND])

            self.ast_builder.down(ASTNode, [TT.AND])

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
            self._atom()
        else:
            raise SyntaxError("logic operand", self.LT(1))

    def _atom(self):
        """atomic formula

        :grammar: <code_ae> <comp_op> <code_ae>
        :returns: None
        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.COMP_OP])

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
        savestate_node = self.ast_builder.down(ASTNode, [TT.NOT])

        while True:
            self.match_and_add(TT.NOT)

            if self.LTT(1) != TT.NOT:
                break

            self.ast_builder.down(ASTNode, [TT.NOT])

        self._code_le()

        self.ast_builder.up(savestate_node)
