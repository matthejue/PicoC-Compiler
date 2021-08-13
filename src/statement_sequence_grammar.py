from assignment_allocation_grammar import AssignmentAllocationGrammar
# from abstract_syntax_tree import ASTNode
from lexer import TT


class StatementSequenceGrammar(AssignmentAllocationGrammar):

    """The statement sequence part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)

    def code_ss(self):
        """statement sequence startpoint

        :grammar: <ss>
        :returns: None

        """
        self._ss()

    def _ss(self):
        """statement sequence

        :grammar: (<s>?)+
        :returns: None

        """
        while True:
            if self._is_statement():
                self._s()

            # TODO: add in other statement types by replacing the false
            # it's possibe to write var = 10;;
            if not (self._is_statement() or self.LTT(1) == TT.SEMICOLON):
                break

    def _s(self):
        """statement

        :grammar: <code_aa> | ...
        :returns: None

        """
        if self._is_assignment():
            self.code_aa()
        # TODO: elif ...
        else:
            raise SyntaxError("statement", self.LT(1))

    def _is_assignment(self):
        """Test whether the next statement is a assignment.

        :returns: boolean

        """
        return self.LTT(2) == TT.ASSIGNMENT or\
            (self.LTT(1) == TT.PRIM_DT and self.LTT(2) == TT.IDENTIFIER)

    def _is_statement(self):
        return self._is_assignment() or False
