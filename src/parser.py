from errors import SyntaxError
from ast_builder import ASTBuilder
from abstract_syntax_tree import TokenNode


class Parser:

    """Analyzes the syntactic structure of a token sequence generated by the
    Lexer using  k>1 lookahead tokens
    """

    def __init__(self, lexer, num_lts):
        """
        :lts: lookahead tokens
        :num_lts: number of lookahead tokens
        :lt_idx: lookahead token index

        """
        self.lexer = lexer
        self.num_lts = num_lts
        self.lts = [0] * self.num_lts
        self.lt_idx = 0
        for _ in range(self.num_lts):
            self.next_token()
        self.ast_builder = ASTBuilder()

    def next_token(self):
        """fills next position in the lookahead tokenlist with token

        :returns: None
        """
        self.lts[self.lt_idx] = self.lexer.next_token()
        self.lt_idx = (self.lt_idx + 1) % self.num_lts

    def LT(self, i):
        """Lookahead Token

        :returns: find out token looking ahead i tokens
        """
        return self.lts[(self.lt_idx + i - 1) % self.num_lts]

    def LTT(self, i):
        """Lookahead tokentype

        :returns: find out type locking ahead i tokens
        """
        return self.LT(i).type

    def match(self, tts):
        """Check if one of the tts are the next token in the lexer to match. In
        general checks if non-terminal symbols are at the right syntactial
        position

        :tts: possibly matching tokentypes (because of symbols like e.g. '-')
        :returns: None, possibly an exception
        """
        if (self.LTT(1) in tts):
            self.next_token()
        else:
            raise SyntaxError("'" + tts.value + "'", self.LT(1))

    def match_and_add(self, tts):
        """Add the current token to the ast and check for match

        :tts: possibly matching tokentypes (because of symbols like e.g. '-')
        :returns: None, possibly an exception
        """
        # if (self.ast_builder.current_node.token not in tts):
        self.ast_builder.addChild(TokenNode(self.LT(1)))
        self.match(tts)