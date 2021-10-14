from errors import InvalidCharacterError
from enum import Enum
import string
import globals


class Token():

    """Identifies what a certiain string slice is"""

    def __init__(self, type, value, position):
        """
        :position: (row, column) in the file where the token starts
        """
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        if globals.args.verbose:
            return f"<{self.type},'{self.value}',{self.position}>"
        return f"'{self.value}'"


class TT(Enum):

    """Tokentypes that are part of the grammar. Their strings are used for
    differentiation and for error messages"""

    EOF = "end of file"
    UNARY_OP = "unary operator"
    BINOP_PREC_1 = "binary operator with precedence 1"
    BINOP_PREC_2 = "binary operator with precedence 2"
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
        elif (self.lc_col + 1 == len(self.input[self.lc_row]) and
              self.lc_row + 1 < len(self.input)):
            self.lc_row += 1
            self.lc_col = 0
        elif (self.lc_col + 1 == len(self.input[self.lc_row]) and
              self.lc_row + 1 == len(self.input)):
            self.lc_col += 1
        else:
            pass

        # next character
        if (self.lc_row + 1 == len(self.input) and
                self.lc_col == len(self.input[self.lc_row])):
            self.c = self.lc
            self.lc = self.EOF_CHAR
        else:
            self.c = self.lc
            self.lc = self.input[self.lc_row][self.lc_col]

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

        return Token(TT.NUMBER, number, self.position)

    def _identifier_special_keyword(self):
        """

        :grammar: <identifier> | <if> | <else> | <while> | <do> | <int>
        | <char>
        :returns: Identifier Token
        """
        # check for special keywords
        token = self._check_word(TT.IF, "if")
        if token:
            return token
        token = self._check_word(TT.ELSE, "else")
        if token:
            return token
        token = self._check_word(TT.WHILE, "while")
        if token:
            return token
        token = self._check_word(TT.DO_WHILE, "do")
        if token:
            return token
        token = self._check_word(TT.PRIM_DT, "int")
        if token:
            return token
        token = self._check_word(TT.PRIM_DT, "char")
        if token:
            return token
        token = self._check_word(TT.PRIM_DT, "void")
        if token:
            return token
        token = self._check_word(TT.CONST, "const")
        if token:
            return token
        token = self._check_word(TT.MAIN, "main")
        if token:
            return token

        # nothing more left then being a identifier
        # TOOD: that could be programmed more efficient by keeping the old word
        return self._identifier()

    def _check_word(self, tokentype, word):
        # TODO: word und tokentype umdrehe, damit es zu Token passt
        """if

        :grammar: <word>
        :returns: None

        """
        lc_row_copy, lc_col_copy, c_copy, lc_copy = self.lc_row, self.lc_col,\
            self.c, self.lc

        for match_char in word:
            if self.lc != match_char:
                break
            self.next_char()
        else:
            if self.lc not in self.LETTER_DIGIT:
                return Token(tokentype, word, self.position)

        self.lc_row, self.lc_col, self.c, self.lc = lc_row_copy, lc_col_copy,\
            c_copy, lc_copy

    def _identifier(self):
        """identifier

        :grammar: <letter> <letter_digit>*
        :returns: None

        """
        self.next_char()
        word = self.c
        while self.lc in self.LETTER_DIGIT:
            self.next_char()
            word += self.c

        return Token(TT.IDENTIFIER, word, self.position)

    def _not(self, ):
        """

        :grammar: '!''='?
        :returns: None

        """
        self.next_char()
        if self.lc == '=':
            self.next_char()
            return Token(TT.COMP_OP, '!=', self.position)
        return Token(TT.NOT, self.c, self.position)

    def _and(self):
        """

        :grammar: &&?
        :returns: None

        """
        self.next_char()
        if self.lc == '&':
            self.next_char()
            return Token(TT.AND, "&&", self.position)
        return Token(TT.BINOP_PREC_1, self.c, self.position)

    def _or(self):
        """

        :grammar: '|''|'?
        :returns: None

        """
        self.next_char()
        if self.lc == '|':
            self.next_char()
            return Token(TT.OR, "||", self.position)
        return Token(TT.BINOP_PREC_1, self.c, self.position)

    def _comp_operator_assignment_bitshift(self):
        """

        :grammar: ((==?)|(<(<|=)?)|(>(>|=)?))
        :returns: None
        """
        if self.lc == '=':
            self.next_char()
            if self.lc == '=':
                self.next_char()
                return Token(TT.COMP_OP, "==", self.position)
            return Token(TT.ASSIGNMENT, '=', self.position)
        elif self.lc == '<':
            self.next_char()
            if self.lc == '=':
                self.next_char()
                return Token(TT.COMP_OP, "<=", self.position)
            elif self.lc == '<':
                self.next_char()
                return Token(TT.BITSHIFT, "<<", self.position)
            return Token(TT.COMP_OP, self.c, self.position)
        elif self.lc == '>':
            self.next_char()
            if self.lc == '=':
                self.next_char()
                return Token(TT.COMP_OP, ">=", self.position)
            elif self.lc == '>':
                self.next_char()
                return Token(TT.BINOP_PREC_1, ">>", self.position)
            return Token(TT.COMP_OP, self.c, self.position)

    def _division_sign_or_comment(self, ):
        """

        :grammar: /(/|('*'.*'*'/))?
        :returns: None
        """
        self.next_char()
        if self.lc == '/':
            # don't go one position over last character else one gets stuck at
            # this line forever because a character > line end can only be
            # triggered at the end of the code
            self.lc_col = len(self.input[self.lc_row]) - 1
            self.next_char()
        elif self.lc == '*':
            while not (self.lc == '/' and self.c == '*' or
                       self.lc == self.EOF_CHAR):
                self.next_char()
            self.next_char()
        else:
            return Token(TT.BINOP_PREC_1, self.c, self.position)
