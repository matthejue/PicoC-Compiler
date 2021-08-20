from abstract_syntax_tree import ASTNode
from lexer import TT
from errors import NoApplicableRuleError


def code_ie(self, ):
    self.if_()


def if_(self, ):
    """if

    :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) <else>?
    :returns: None
    """
    savestate_node = self.ast_builder.down(ASTNode, [TT.IF])

    self.match_and_add([TT.IF])

    self.match([TT.L_PAREN])

    self.code_le()

    self.match([TT.R_PAREN])

    if self.LTT(1) == TT.L_BRACE:
        self.match([TT.L_BRACE])

        self.code_ss()

        self.match([TT.R_BRACE])
    elif self._is_statement():
        self._s()
    else:
        raise NoApplicableRuleError(
            "statement in braces or single statement", self.LT(1))

    if self.LTT(1) == TT.ELSE:
        self.else_()

    self.ast_builder.up(savestate_node)


def else_(self, ):
    """else:

    :grammar:
    :returns: else ({ <code_ss> }|<s>)
    """
    savestate_node = self.ast_builder.down(ASTNode, [TT.ELSE])

    self.match_and_add([TT.ELSE])

    if self.LTT(1) == TT.L_BRACE:
        self.match([TT.L_BRACE])

        self.code_ss()

        self.match([TT.R_BRACE])
    elif self._is_statement():
        self._s()
    else:
        raise NoApplicableRuleError(
            "statement in braces or single statement", self.LT(1))

    self.ast_builder.up(savestate_node)
