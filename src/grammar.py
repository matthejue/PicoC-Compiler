from file_grammar import FileGrammar
from lexer import TT


class Grammar(FileGrammar):
    """the function part of the context free grammar of the piocC
    language"""
    def __init__(self, lexer):
        super().__init__(lexer)

        # to check for the MoreThanOneMainFunctionError
        self.mains = []

    def start_parse(self):
        """start parsing the grammar

        :returns: None
        """
        self.code_fi()
        self.match([TT.EOF])

    def reveal_ast(self):
        """makes the abstract syntax tree of the grammar available

        :returns: rootnode of the abstract syntax tree
        """
        return self.ast_builder.root

    def __repr__(self, ):
        return str(self.ast_builder)
