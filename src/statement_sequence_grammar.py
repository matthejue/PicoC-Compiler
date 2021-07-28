from assignment_allocation_grammar import AssignmentAllocationGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT


class StatementSequenceGrammar(AssignmentAllocationGrammar):

    """The statement sequence part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_ss(self):
        """statement sequence startpoint

        :grammar:
        :returns: None

        """
        self.ss()

    def ss(self):
        """statement sequence

        :grammar: (<s> ;)+
        :returns: None

        """
        while True:
            self.s()
            self.match([TT.SEMICOLON])

            if self.LTT(1) != TT.ASSIGNMENT:
                break

    def s(self):
        """statement

        :grammar: <code_aa> | ...
        :returns: None

        """
        if self.LTT(2) == TT.ASSIGNMENT or self.LTT(3) == TT.ASSIGNMENT:
            self.code_aa()
        else:
            raise SyntaxError(
                "statement", self.LT(1))
