from errors import IllegalCharacterError
from tok import Metadata, Token
from tokentypes import *  # pylint: disable=unused-wildcard-import

###############################################################################
#                                    Lexer                                    #
###############################################################################


class Lexer:
    """Splits input into tokens."""

    def __init__(self, fname, code):
        self.md = Metadata(-1, 0, fname, code)
        self.next_char()

    def next_char(self):
        """Goes to the next_char character
        :returns: None

        """
        if self.md.col < len(self.md.code[self.md.row]):
            self.md.col += 1

        # handle carriage return
        if self.md.col == len(self.md.code[self.md.row]) \
                and self.md.row + 1 < len(self.md.code):
            self.md.col = 0
            self.md.row += 1

        # get character with corresponding index if end of file not reached
        self.md.current_char = self.md.code[self.md.row][self.md.col] \
            if self.md.col < len(self.md.code[self.md.row]) else 'EOF'

    def create_tokens(self):
        """Creates tokens out of the string.
        :returns: List of Tokens

        """
        tokens = []

        while self.md.current_char != 'EOF':
            if self.md.current_char in " \t":
                self.next_char()
            elif self.md.current_char == ';':
                tokens += [Token(T_SEMICOLON, self.md.copy())]
                self.next_char()
            elif self.md.current_char in DIGITS:
                constant = ""

                while self.md.current_char in DIGITS_WITH_ZERO:
                    constant += self.md.current_char
                    self.next_char()

                tokens += [Token(T_CONSTANT, self.md.copy(int(constant)))]
            elif self.md.current_char in LETTERS:
                identifier = ""

                while self.md.current_char in LETTERS_DIGITS:
                    identifier += self.md.current_char
                    self.next_char()

                tokens += [Token(T_IDENTIFIER, self.md.copy(identifier))]
            elif self.md.current_char in BINOPS:
                if self.md.current_char == '-':
                    tokens += [Token([T_UNOP, T_BINOP, T_PRECEDENCE_2],
                                     self.md.copy())]
                else:
                    if self.md.current_char in OP_PRECEDENCE_1:
                        tokens += [Token([T_BINOP, T_PRECEDENCE_1],
                                         self.md.copy())]
                    else:  # self.current_char in OP_PRECEDENCE_2:
                        tokens += [Token([T_BINOP, T_PRECEDENCE_2],
                                         self.md.copy())]
                self.next_char()
            elif self.md.current_char in UNOPS:  # for ~ operator
                tokens += [Token(T_UNOP, self.md.copy())]
                self.next_char()
            elif self.md.current_char == '(':
                tokens += [Token(T_L_PAREN, self.md.copy())]
                self.next_char()
            elif self.md.current_char == ')':
                tokens += [Token(T_R_PAREN, self.md.copy())]
                self.next_char()
            elif self.md.current_char == '=':
                tokens += [Token(T_EQUAL, self.md.copy())]
                self.next_char()
            else:
                char = self.md.current_char
                return [], IllegalCharacterError(self.md.copy(), char)
        return tokens + [Token(T_EOF, self.md.copy())], None
