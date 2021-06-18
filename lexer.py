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
                tokens, error = self._create_number(tokens)

                if error:
                    return [], error
            elif self.md.current_char in LETTERS:
                tokens, error = self._create_word(tokens)

                if error:
                    return [], error
            elif self.md.current_char in BINOPS:
                tokens = self._deal_with_binops(tokens)
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

    def _create_number(self, tokens):
        """creates a number for the Lexer

        :returns: tokens, error

        """
        constant = ""

        while True:
            if self.md.current_char in " " or self.md.col >= len(self.md.code[self.md.row]):
                break
            elif self.md.current_char not in DIGITS_WITH_ZERO:
                char = self.md.current_char
                return [], IllegalCharacterError(self.md.copy(), char)
            constant += self.md.current_char
            self.next_char()

        tokens += [Token(T_CONSTANT, self.md.copy(int(constant)))]
        return tokens, None

    def _create_word(self, tokens):
        """creates a word for the Lexer

        :returns: tokens, error

        """
        identifier = ""

        while True:
            if self.md.current_char in " " or self.md.col >= len(self.md.code[self.md.row]):
                break
            elif self.md.current_char not in LETTERS_DIGITS:
                char = self.md.current_char
                return [], IllegalCharacterError(self.md.copy(), char)
            identifier += self.md.current_char
            self.next_char()

        tokens += [Token(T_IDENTIFIER, self.md.copy(identifier))]
        return tokens, None

    def _deal_with_binops(self, tokens):
        """deals with binary operators for the lexer

        :returns: tokens

        """
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
        return tokens
