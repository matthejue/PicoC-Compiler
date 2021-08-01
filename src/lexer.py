from errors import SyntaxError, InvalidCharacterError
from enum import Enum
import string
import globals


class Token():

    """Identifies what a certiain string slice is"""

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        if globals.args.verbose:
            return f"<{self.type},'{self.value}'>"
        return f"'{self.value}'"


class TT(Enum):

    """Tokentypes that are part of the grammar"""

    ROOT = "ROOT"
    EOF = "EOF"
    NUMBER = "number"
    WORD = "word"
    UNARY_OP = "unary operator"
    BINOP_PREC_1 = "binary operator with precedence 1"
    BINOP_PREC_2 = "binary operator with precedence 2"
    ASSIGNMENT = "="
    L_PAREN = "("
    R_PAREN = ")"
    SEMICOLON = ";"
    MINUS = "-"
    ALLOC = "allocation"
    STATEMENT = "statement"
    FUNCTION = "function"
    NOT = "not operator or not as part of logical expression grammar"
    AND_OP = "and operator"
    OR_OP = "or operator"
    NOT = "not as part of logical expression grammar"
    AND = "and as part of logical expression grammar"
    OR = "or as part of logical expression grammar"


class Lexer:

    """Identifies tokens in the picoC code

    :Info: The Lexer doesn't check if the token is also at the right position
    to follow the grammar rules (that's the task of the parser). That's why
    12ab will be split into a number an identifier Token and it's the task of
    the Parser to raise an error. That's also the reason why self.next_char()
    is used instead of self.match()
    """

    EOF_CHAR = "EOF"
    DIGIT_WITHOUT_ZERO = "123456789"
    DIGIT_WITH_ZERO = "0123456789"
    LETTER = string.ascii_letters
    LETTER_DIGIT = LETTER + DIGIT_WITH_ZERO + '_'
    COMP_OPERATOR = ['==', '<=', '>=', '<', '>']

    def __init__(self, fname, input):
        """
        :lc: lookahead character
        :c: character

        """
        self.fname = fname
        self.input = input
        self.c_idx = 0
        self.lc = input[self.c_idx]
        self.c = None

    def next_token(self):
        """identifies the next Token in the picoC code

        :returns: Token

        """
        while self.lc != self.EOF_CHAR:
            # TODO: remove \n again
            if self.lc in ' \t':
                self.next_char()
            elif self.lc == ';':
                self.next_char()
                return Token(TT.SEMICOLON, self.c)
            elif self.lc in '*/':
                self.next_char()
                return Token(TT.BINOP_PREC_1, self.c)
            elif self.lc == '+':
                self.next_char()
                return Token(TT.BINOP_PREC_2, self.c)
            elif self.lc == '-':
                # minus has a special role because it can be both a unary and
                # binary operator
                self.next_char()
                return Token(TT.MINUS, self.c)
            elif self.lc == '~':
                # minus has a special role because it can be both a unary and
                # binary operator
                self.next_char()
                return Token(TT.UNARY_OP, self.c)
            elif self.lc == '(':
                self.next_char()
                return Token(TT.L_PAREN, self.c)
            elif self.lc == ')':
                self.next_char()
                return Token(TT.R_PAREN, self.c)
            elif self.lc in self.DIGIT_WITHOUT_ZERO:
                return self._number()
            elif self.lc in self.LETTER:
                return self._word()
            elif self.lc == "=":
                self.next_char()
                return Token(TT.ASSIGNMENT, self.c)
            elif self.lc == "!":
                self.next_char()
                return Token(TT.NOT, self.c)
            elif self.lc == "&":
                return self._and()
            elif self.lc == "|":
                return self._or()
            elif self.lc in self.COMP_OPERATOR:
                return self._comp_operator()
            else:
                raise InvalidCharacterError(self.lc)
        return Token(TT.EOF, self.lc)

    def next_char(self):
        """go to the next character, detect if "end of file" is reached

        :returns: None

        """
        self.c_idx += 1
        if self.c_idx >= len(self.input):
            self.c = self.lc
            self.lc = self.EOF_CHAR
        else:
            self.c = self.lc
            self.lc = self.input[self.c_idx]

    def match(self, m):
        """Check if m is the next character in the input to match

        :m: possibly matching character
        :returns: None

        """
        if self.lc == m:
            self.next_char()
        else:
            raise SyntaxError(m, self.c)

    def _number(self):
        """

        :grammar: <digit_without_zero> <digit_with_zero>*
        :returns: Number Token

        """
        self.next_char()
        number = self.c
        while self.lc in self.DIGIT_WITH_ZERO:
            self.next_char()
            number += self.c

        return Token(TT.NUMBER, int(number))

    def _word(self):
        """

        :grammar: <letter> <letter_digit>*
        :returns: Identifier Token

        """
        self.next_char()
        word = self.c
        while self.lc in self.LETTER_DIGIT:
            self.next_char()
            word += self.c

        return Token(TT.WORD, word)

    def _and(self):
        """

        :grammar: &&?
        :returns: None

        """
        self.next_char()
        if self.lc == '&':
            self.next_char()
            return Token(TT.AND, self.c)
        return Token(TT.AND_OP, self.c)

    def _or(self):
        """

        :grammar: '|''|'?
        :returns: None

        """
        self.next_char()
        if self.lc == '|':
            self.next_char()
            return Token(TT.OR, self.c)
        return Token(TT.OR_OP, self.c)

    def _comp_operator(self):
        """

        :grammar: == | <=? | >=?
        :returns: None

        """
