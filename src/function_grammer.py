from arithmetic_expression_grammer import ArithmeticExpressionGrammer
from abstract_syntax_tree import ASTNode
from lexer import TT


class FunctionGrammer(ArithmeticExpressionGrammer):

    """the function part of the context free grammer of the piocC
    language"""

    def __init__(self, lexer, num_lts):
        super().__init__(lexer, num_lts)

    def start_parse(self):
        """start parsing the grammer

        :returns: None

        """
        self.ast_builder.down(ASTNode, [TT.ROOT])
        self.code_ae()
