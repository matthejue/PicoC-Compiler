from arithmetic_expression_grammar import ArithmeticExpressionGrammar


class LogicExpressionGrammar(ArithmeticExpressionGrammar):

    """The logic expression part of the context free grammar of the piocC
    language"""

    def __init__(self):
        pass

    def code_le(self):
        """logic expression startpoint

        :grammar: <le>
        :returns: None

        """
        pass

    def le(self):
        """logic expression

        :grammar: !<le>
        :returns: None

        """
        pass
