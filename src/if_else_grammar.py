from abstract_syntax_tree import IfNode, IfElseNode
from lexer import TT
from errors import NoApplicableRuleError, MismatchedTokenError


def code_ie(self, ):
    self.code_if_if_else()


def code_if_if_else(self):
    """if or if else

    :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) (else ({
    <code_ss> }|<s>))?
    :returns: None
    """
    if self.taste(self._if_else):
        self._if_else()
    elif self.taste(self._taste_consume_if_without_else):
        self._taste_consume_if_without_else()
    else:
        self._handle_all_tastes_unsuccessful("if or if else expression")


def _taste_consume_if_without_else(self):
    """taste whether the next expression is a if without else

    :grammar: <if_without_else>
    :returns: None
    """
    self._if_without_else()
    if self.LTT(1) == TT.ELSE:
        raise MismatchedTokenError("if", self.LT(1))


# def taste_consume_if_else():
#     """taste whether the next expression is a if else
#
#     :grammar: <if_else>
#     :returns: None
#     """
#     self._if_else()


def _if_without_else(self, ):
    """if

    :grammar: if '('<code_le>')' ({ <code_ss> }|<s>)
    :returns: None
    """
    savestate_node = self.ast_builder.down(IfNode, [TT.IF])

    self._if()

    self.ast_builder.up(savestate_node)


def _if_else(self, ):
    """if else

    :grammar: if '('<code_le>')' ({ <code_ss> }|<s>) else ({ <code_ss> }|<s>)
    :returns: None
    """
    savestate_node = self.ast_builder.down(IfElseNode, [TT.IF])

    self._if()
    # savestate_node = self.ast_builder.down(IfElseNode, [TT.ELSE])

    # self.match_and_add([TT.ELSE])
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


def _if(self):
    """if code piece

    :grammar: if '('<code_le>')' ({ <code_ss> }|<s>)
    :returns: None
    """
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
