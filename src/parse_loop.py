from loop_nodes import While, DoWhile
from lexer import TT


class LoopParser:
    def parse_loop(self):
        """loop grammar startpoint

        :grammar: <loop>
        :returns: None
        """
        self._loop()

    def _loop(self):
        """loop

        :grammar: <while> | <do_while>
        :returns: None
        """
        if self.LTT(1) == TT.WHILE:
            self._while()
        elif self.LTT(1) == TT.DO:
            self._do_while()
        #  else: Error can't happen

    def _while(self):
        """while loop

        :grammar: <while> ( <code_le> ) { <code_ss> }
        :returns: None
        """
        savestate_node = self.ast_builder.down(While)

        self.consume_next_token()  # [TT.WHILE]

        self.match([TT.L_PAREN])

        self.parse_logic_exp()

        self.match([TT.R_PAREN])

        self.match([TT.L_BRACE])

        self.parse_stmts()

        self.match([TT.R_BRACE])

        self.ast_builder.up(savestate_node)

    def _do_while(self):
        """do while loop

        :grammar: do { <code_ss> } while ( <code_le> ) ;
        :returns: None
        """
        savestate_node = self.ast_builder.down(DoWhile)

        self.consume_next_token()  # [TT.DO]

        self.match([TT.L_BRACE])

        self.parse_stmts()

        self.match([TT.R_BRACE])

        self.match([TT.WHILE])

        self.match([TT.L_PAREN])

        self.parse_logic_exp()

        self.match([TT.R_PAREN])

        self.match([TT.SEMICOLON])

        self.ast_builder.up(savestate_node)
