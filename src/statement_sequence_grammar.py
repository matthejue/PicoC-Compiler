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

        :grammar: <ss>
        :returns: None

        """
        self.ss()

    def ss(self):
        """statement sequence

        :grammar: (<s>? ;)+
        :returns: None

        """
        while True:
            self.s()
            self.match([TT.SEMICOLON])

            # TODO: add in other statement types by replacing the false
            if not (self.is_assignment() or False):
                break

    def s(self):
        """statement

        :grammar: <code_aa> | ...
        :returns: None

        """
        if self.is_assignment():
            self.code_aa()
        # TODO: elif ...
        else:
            raise SyntaxError("statement", self.LT(1))

    def is_assignment(self):
        """Test whether the next statement is a assignment.

        :returns: boolean

        """
        return self.LTT(2) == TT.ASSIGNMENT or self.LTT(3) == TT.ASSIGNMENT
