from errors import SyntaxError, InvalidCharacterError
from enum import Enum
import string


class Token():

    """Identifies what a certiain string slice is"""

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"<{self.type},'{self.value}'>"


class TT(Enum):

    """Tokentypes that are part of the grammer"""

    EOF = "EOF"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    UNOP = "UNOP"
    BINOP_PREC_1 = "BINOP_PREC_1"
    BINOP_PREC_2 = "BINOP_PREC_2"
    EQUALS = "EQUALS"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    SEMICOLON = "SEMICOLON"


class Lexer:

    """Identifies tokens in the picoC code

    :Info: The Lexer doesn't check if the token is also at the right position
    to follow the grammer rules (that's the task of the parser). That's why
    12ab will be split into a number an identifier Token and it's the task of
    the Parser to raise an error. That's also the reason why self.next_char()
    is used instead of self.match()
    """

    EOF_CHAR = "EOF"
    DIGIT_WITHOUT_ZERO = "123456789"
    DIGIT_WITH_ZERO = "0123456789"
    LETTER = string.ascii_letters
    LETTER_DIGIT = LETTER + DIGIT_WITH_ZERO + '_'

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
        """identifies the next Token

        :returns: Token

        """
        while self.lc != self.EOF_CHAR:
            if self.lc in ' \t':
                self.next_char()
            elif self.lc == ';':
                self.next_char()
                return Token(TT.SEMICOLON, self.c)
            elif self.lc in '*/':
                self.next_char()
                return Token(TT.BINOP_PREC_1, self.c)
            elif self.lc in '+-':
                self.next_char()
                return Token(TT.BINOP_PREC_2, self.c)
            elif self.lc == '(':
                self.next_char()
                return Token(TT.L_PAREN, self.c)
            elif self.lc == ')':
                self.next_char()
                return Token(TT.R_PAREN, self.c)
            elif self.lc in self.DIGIT_WITHOUT_ZERO:
                return self._number()
            elif self.lc in self.LETTER:
                return self._identifier()
            elif self.lc == "=":
                self.next_char()
                return Token(TT.EQUALS, self.c)
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

        :grammer: <digit_without_zero> <digit_with_zero>*
        :returns: Number Token

        """

        self.next_char()
        number = self.c
        while self.lc in self.DIGIT_WITH_ZERO:
            self.next_char()
            number += self.c

        return Token(TT.NUMBER, int(number))

    def _identifier(self):
        """

        :grammer: <letter> <letter_digit>*
        :returns: Identifier Token

        """
        self.next_char()
        identifier = self.c
        while self.lc in self.LETTER_DIGIT:
            self.next_char()
            identifier += self.c

        return Token(TT.IDENTIFIER, identifier)
