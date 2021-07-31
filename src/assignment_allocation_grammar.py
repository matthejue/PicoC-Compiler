from arithmetic_expression_grammar import ArithmeticExpressionGrammar
from abstract_syntax_tree import ASTNode
from lexer import TT


class AssignmentAllocationGrammar(ArithmeticExpressionGrammar):
    """The assignment expression part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def code_aa(self):
        """assignment and allocation startpoint

        :grammar: <aa>
        :returns: None

        """
        self.aa()

    def aa(self):
        """assignment and allocation

        :grammar: #2 <alloc> | ((<word> | <alloc>) = #2 (<word> = #2)* <ae>)
        :returns: None

        """
        savestate_node = self.ast_builder.down(
            ASTNode, [TT.STATEMENT, TT.ASSIGNMENT])

        if self.LTT(2) == TT.ASSIGNMENT:
            self.match_and_add([TT.WORD])
        elif self.LTT(3) == TT.ASSIGNMENT:
            self.alloc()
        else:
            raise SyntaxError(
                "identifier or assignment expression", self.LT(2))

        self.match_and_add([TT.ASSIGNMENT])

        self.ast_builder.down(ASTNode, [TT.ASSIGNMENT])

        while self.LTT(2) == TT.ASSIGNMENT:
            self.match_and_add([TT.WORD])

            self.match_and_add([TT.ASSIGNMENT])

            self.ast_builder.down(ASTNode, [TT.ASSIGNMENT])

        self.code_ae()

        self.ast_builder.up(savestate_node)

    def alloc(self):
        """allocation of a variable

        :grammar: #2 <word> <word> (= <va>)?
        :returns: None

        """
        savestate_node = self.ast_builder.down(ASTNode, [TT.ALLOC, TT.WORD])

        self.match_and_add([TT.WORD])
        self.match_and_add([TT.WORD])

        self.ast_builder.up(savestate_node)
