from function_grammar import FunctionGrammar


class Grammar(FunctionGrammar):

    """the function part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def start_parse(self):
        """start parsing the grammar

        :returns: None

        """
        if self.lexer.input == "var = 12 > 3;":
            if self.lexer.input == "var = 12 > 3;":
                pass
        self.code_f()

    def reveal_ast(self):
        """makes the abstract syntax tree of the grammar available

        :returns: rootnode of the abstract syntax tree

        """
        return self.ast_builder.root
