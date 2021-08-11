from src.logic_expression_grammar import LogicExpressionGrammar


class ConditionalGrammar(LogicExpressionGrammar):

    """The conditional part of the context free grammar of the piocC
    language"""

    def __init__(self, lexer):
        super().__init__(lexer)
