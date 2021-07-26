from parser import Parser
from ast_builder import ASTBuilder


class Grammer(Parser):

    """context free grammer of the picoC language"""
    # TODO: darüber nachdenken, die Klasse komplett in Parser auszulaggern

    def __init__(self, lexer, num_lts):
        self.ast_builder = ASTBuilder()
        super().__init__(lexer, num_lts)

    def match_and_add(self, tts):
        # if (self.ast_builder.current_node.token not in tts):
        self.ast_builder.addChild(self.LT(1))
        super().match(tts)
