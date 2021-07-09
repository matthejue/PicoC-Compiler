from parser import Parser
from ast_builder import ASTBuilder


class Grammer(Parser):

    """context free grammer of the picoC language"""

    def __init__(self, lexer, num_lts):
        self.ast_builder = ASTBuilder()
        super().__init__(lexer, num_lts)

    # def match(self, tt):
        # self.ast_builder.addChild(self.LT(1))
        # super().match(tt)
