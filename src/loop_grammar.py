from abstract_syntax_tree import LoopNode
from lexer import TT
# from errors import NoApplicableRuleError


def code_lo(self):
    """loop grammar startpoint

    :grammar: <loop>
    :returns: None
    """
    self.loop()


def loop(self):
    """loop

    :grammar: <while> | <do_while>
    :returns: None
    """
    if self.LTT(1) == TT.WHILE:
        self.while_()
    elif self.LTT(1) == TT.DO_WHILE:
        self.do_while()
    # eigentlich ergibt hier der Error keinen Sinnn, weil er nie
    # aufgerufen werden kann
    # else:
    #     raise NoApplicableRuleError('while or do while', self.LT(1))


def while_(self):
    """while loop

    :grammar: <while> ( <code_le> ) { <code_ss> }
    :returns: None
    """
    savestate_node = self.ast_builder.down(LoopNode, [TT.WHILE])

    self.match_and_add([TT.WHILE])

    self.match([TT.L_PAREN])

    self.code_le()

    self.match([TT.R_PAREN])

    self.match([TT.L_BRACE])

    self.code_ss()

    self.match([TT.R_BRACE])

    self.ast_builder.up(savestate_node)


def do_while(self):
    """do while loop

    :grammar: do { <code_ss> } while ( <code_le> ) ;
    :returns: None
    """
    savestate_node = self.ast_builder.down(LoopNode, [TT.DO_WHILE])

    self.match_and_add([TT.DO_WHILE])

    self.match([TT.L_BRACE])

    self.code_ss()

    self.match([TT.R_BRACE])

    self.match([TT.WHILE])

    self.match([TT.L_PAREN])

    self.code_le()

    self.match([TT.R_PAREN])

    self.match([TT.SEMICOLON])

    self.ast_builder.up(savestate_node)
