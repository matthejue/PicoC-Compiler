from errors import InvalidCharacterError
from enum import Enum
import string
import global_vars


class Token():
    """Identifies what a certiain string slice is"""

    __match_args__ = ("type")

    def __init__(self, type, value, position):
        """
        :type: TT
        :value: string
        :position: (row, column) in the file where the token starts
        """
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        if global_vars.args.verbose:
            return f"<{self.type},'{self.value}',{self.position}>"
        return f"'{self.value}'"


class TT(Enum):
    """Tokentypes that are part of the grammar. Their strings are used for
    differentiation and for error messages"""

    EOF = "end of file"
    UNARY_OP = "unary operator"
    BINOP_PREC_1 = "binary operator with precedence 1"
    BINOP_PREC_2 = "binary operator with precedence 2"
    PLUS_OP = "+"
    MINUS_OP = "-"
    MUL_OP = "-"
    DIV_OP = "/"
    MOD_OP = "%"
    OPLUS_OP = "^"
    ASSIGNMENT = "="
    L_PAREN = "("
    R_PAREN = ")"
    L_BRACE = "{"
    R_BRACE = "}"
    SEMICOLON = ";"
    MINUS = "-"
    ALLOC = "allocation"
    STATEMENT = "statement"
    FUNCTION = "function"
    NOT = "!"
    AND_OP = "&"
    OR_OP = "|"
    AND = "&&"
    OR = "||"
    COMP_OP = "comparison operator"
    NUMBER = "number"
    CHAR = "character"
    IDENTIFIER = "identifier"
    CONST = "constant qualifier"
    VAR = "variable qualifier"
    PRIM_DT = "primitive datatype"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO_WHILE = "do while"
    MAIN = "main function"
    TO_BOOL = "convert to boolean value"


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
    LETTER_DIGIT_SPACE = LETTER_DIGIT + ' '
    COMP_OPERATOR_ASSIGNMENT_BITSHIFT = ['=', '<', '>']

    def __init__(self, fname, input):
        """
        :lc: lookahead character
        :c: character

        """
        self.fname = fname
        self.input = input
        self.lc_col = 0
        self.lc_row = 0
        self.lc = input[self.lc_row][self.lc_col]
        self.c = None
        # position variable to be available between methods
        self.position = (0, 0)

    def next_token(self):
        """identifies the next Token in the picoC code

        :returns: Token
        """
        while self.lc != self.EOF_CHAR:
            self.position = (self.lc_row, self.lc_col)
            # TODO: remove \n again
            if self.lc in ' \t':
                self.next_char()
            elif self.lc == ';':
                self.next_char()
                return Token(TT.SEMICOLON, self.c, self.position)
            elif self.lc in '*%^':
                self.next_char()
                return Token(TT.BINOP_PREC_1, self.c, self.position)
            elif self.lc == '/':
                token = self._division_sign_or_comment()
                if token:
                    return token
            elif self.lc == '+':
                self.next_char()
                return Token(TT.BINOP_PREC_2, self.c, self.position)
            elif self.lc == '-':
                # minus has a special role because it can be both a unary and
                # binary operator
                self.next_char()
                return Token(TT.MINUS, self.c, self.position)
            elif self.lc == '~':
                # minus has a special role because it can be both a unary and
                # binary operator
                self.next_char()
                return Token(TT.UNARY_OP, self.c, self.position)
            elif self.lc == '(':
                self.next_char()
                return Token(TT.L_PAREN, self.c, self.position)
            elif self.lc == ')':
                self.next_char()
                return Token(TT.R_PAREN, self.c, self.position)
            elif self.lc == '{':
                self.next_char()
                return Token(TT.L_BRACE, self.c, self.position)
            elif self.lc == '}':
                self.next_char()
                return Token(TT.R_BRACE, self.c, self.position)
            elif self.lc in self.DIGIT_WITHOUT_ZERO:
                return self._number()
            elif self.lc == "'":
                return self._character()
            elif self.lc == '0':
                self.next_char()
                return Token(TT.NUMBER, self.c, self.position)
            elif self.lc in self.LETTER:
                return self._identifier_special_keyword()
            elif self.lc == '!':
                return self._not()
            elif self.lc == '&':
                return self._and()
            elif self.lc == '|':
                return self._or()
            elif self.lc in self.COMP_OPERATOR_ASSIGNMENT_BITSHIFT:
                return self._comp_operator_assignment_bitshift()
            else:
                raise InvalidCharacterError(self.lc, self.position)
        return Token(TT.EOF, self.lc, self.position)

    def next_char(self):
        """go to the next character, detect if "end of file" is reached

        :returns: None
        """
        # next column or next row
        if self.lc_col + 1 < len(self.input[self.lc_row]):
            self.lc_col += 1
        elif (self.lc_col + 1 == len(self.input[self.lc_row])
              and self.lc_row + 1 < len(self.input)):
            self.lc_row += 1
            self.lc_col = 0
        elif (self.lc_col + 1 == len(self.input[self.lc_row])
              and self.lc_row + 1 == len(self.input)):
            self.lc_col += 1
        else:
            pass

        # next character
        if (self.lc_row + 1 == len(self.input)
                and self.lc_col == len(self.input[self.lc_row])):
            self.c = self.lc
            self.lc = self.EOF_CHAR
        else:
            self.c = self.lc
            self.lc = self.input[self.lc_row][self.lc_col]

    from lexer_2 import _number, _character, _identifier_special_keyword,\
        _check_word, _reached_end_of_line, _identifier, _not, _and, _or,\
        _comp_operator_assignment_bitshift, _division_sign_or_comment
