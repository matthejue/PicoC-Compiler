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

    SEMICOLON = ";"
    PLUS_OP = "+"
    MINUS_OP = "-"
    MUL_OP = "*"
    DIV_OP = "/"
    MOD_OP = "%"
    AND_OP = "&"
    OR_OP = "|"
    OPLUS_OP = "^"
    NOT_OP = "~"
    EQ_COMP = "=="
    UEQ_COMP = "!="
    LT_COMP = "<"
    GT_COMP = ">"
    LE_COMP = "<="
    GE_COMP = ">="
    NOT = "!"
    AND = "&&"
    OR = "||"
    ASSIGNMENT = "="
    L_PAREN = "("
    R_PAREN = ")"
    L_BRACE = "{"
    R_BRACE = "}"
    CONST = "const"  # constant qualifier
    VAR = "var"  # var qualifier
    INT = "int"
    CHAR = "char"
    NUMBER = "number"
    MAIN = "main"
    IF = "if"
    IF_ELSE = "if else"
    WHILE = "while"
    DO_WHILE = "do while"
    IDENTIFIER = "identifier"
    TO_BOOL = "to bool"
    EOF = "end of file"


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
            match self.lc:
                case '\t':
                    self.next_char()
                case ';':
                    self.next_char()
                    return Token(TT.SEMICOLON, self.c, self.position)
                case '+':
                    self.next_char()
                    return Token(TT.PLUS_OP, self.c, self.position)
                case '-':
                    # minus has a special role because it can be both a unary and
                    # binary operator
                    self.next_char()
                    return Token(TT.MINUS_OP, self.c, self.position)
                case '*':
                    self.next_char()
                    return Token(TT.MUL_OP, self.c, self.position)
                case '/':
                    token = self._division_sign_or_comment()
                    if token:
                        return token
                case '%':
                    self.next_char()
                    return Token(TT.MOD_OP, self.c, self.position)
                case '^':
                    self.next_char()
                    return Token(TT.OPLUS_OP, self.c, self.position)
                case '~':
                    # minus has a special role because it can be both a unary and
                    # binary operator
                    self.next_char()
                    return Token(TT.UNARY_OP, self.c, self.position)
                case '(':
                    self.next_char()
                    return Token(TT.L_PAREN, self.c, self.position)
                case ')':
                    self.next_char()
                    return Token(TT.R_PAREN, self.c, self.position)
                case '{':
                    self.next_char()
                    return Token(TT.L_BRACE, self.c, self.position)
                case '}':
                    self.next_char()
                    return Token(TT.R_BRACE, self.c, self.position)
                case self.DIGIT_WITHOUT_ZERO:
                    return self._number()
                case "'":
                    return self._character()
                case '0':
                    self.next_char()
                    return Token(TT.NUMBER, self.c, self.position)
                case self.LETTER:
                    return self._identifier_special_keyword()
                case '!':
                    return self._not()
                case '&':
                    return self._and()
                case '|':
                    return self._or()
                case self.COMP_OPERATOR_ASSIGNMENT_BITSHIFT:
                    return self._comp_operator_assignment_bitshift()
                case _:
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
