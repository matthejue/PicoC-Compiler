from function_grammar import FunctionGrammar
from lexer import TT


class Grammar(FunctionGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def start_parse(self):
        """start parsing the grammar

        :returns: None
        """
        self.code_f()
        self.match([TT.EOF])

    def reveal_ast(self):
        """makes the abstract syntax tree of the grammar available

        :returns: rootnode of the abstract syntax tree
        """
        return self.ast_builder.root
