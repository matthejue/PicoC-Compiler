from errors import SyntaxError, InvalidCharacterError
from enum import Enum
import string
import globals


class Token():

    """Identifies what a certiain string slice is"""

    def __init__(self, type, value, start, end):
        """
        :start: (row, column) in the file where it starts
        :end: (row, column) in the file where it ends
        """
        self.type = type
        self.value = value
        self.start = start
        self.end = end

    def __repr__(self):
        if globals.args.verbose:
            return f"<{self.type},'{self.value}',{self.start},{self.end}>"
        return f"'{self.value}'"


class TT(Enum):

    """Tokentypes that are part of the grammar"""

    EOF = "end of file"
    UNARY_OP = "unary operator"
    BINOP_PREC_1 = "binary operator with precedence 1"
    BINOP_PREC_2 = "binary operator with precedence 2"
    ASSIGNMENT = "assignment operator"
    L_PAREN = "left parenthesis"
    R_PAREN = "right parenthesis"
    L_BRACE = "left brace"
    R_BRACE = "right brace"
    SEMICOLON = "semicolon"
    MINUS = "minus unary or binary operator"
    ALLOC = "allocation"
    STATEMENT = "statement"
    FUNCTION = "function"
    NOT = "not logical expression grammar"
    AND_OP = "and arithmetic operator"
    OR_OP = "or arithmetic operator"
    AND = "and logical expression grammar"
    OR = "or logical expression grammar"
    COMP_OP = "comparison operator"
    BITSHIFT = "bitshift"
    NUMBER = "number"
    IDENTIFIER = "identifier"
    CONST = "constant qualifier"
    VAR = "variable qualifier"
    PRIM_DT = "primitive datatype"
    IF = "if statement"
    ELSE = "else statement"
    WHILE = "while statement"
    DO_WHILE = "do while statement"
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

    def next_token(self):
        """identifies the next Token in the picoC code

        :returns: Token
        """
        while self.lc != self.EOF_CHAR:
            # TODO: remove \n again
            if self.lc in ' \t':
                self.next_char()
            elif self.lc == ';':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.SEMICOLON, self.c, start, end)
            elif self.lc in '*%^':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.BINOP_PREC_1, self.c, start, end)
            elif self.lc == '/':
                token = self._division_sign_or_comment()
                if token:
                    return token
            elif self.lc == '+':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.BINOP_PREC_2, self.c, start, end)
            elif self.lc == '-':
                # minus has a special role because it can be both a unary and
                # binary operator
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.MINUS, self.c, start, end)
            elif self.lc == '~':
                # minus has a special role because it can be both a unary and
                # binary operator
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.UNARY_OP, self.c, start, end)
            elif self.lc == '(':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.L_PAREN, self.c, start, end)
            elif self.lc == ')':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.R_PAREN, self.c, start, end)
            elif self.lc == '{':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.L_BRACE, self.c, start, end)
            elif self.lc == '}':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.R_BRACE, self.c, start, end)
            elif self.lc in self.DIGIT_WITHOUT_ZERO:
                return self._number()
            elif self.lc == '0':
                start, end = ((self.lc_row, self.lc_col) * 2)
                self.next_char()
                return Token(TT.NUMBER, self.c, start, end)
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
                raise InvalidCharacterError(self.lc)
        return Token(TT.EOF, self.lc, start, end)

    def _measure_pos(self, method):
        start = (self.lc_row, self.lc_col)
        method()
        end = (self.lc_row, self.lc_col)
        return (start, end)

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
        start = (self.lc_row, self.lc_col)

        self.next_char()
        number = self.c
        while self.lc in self.DIGIT_WITH_ZERO:
            self.next_char()
            number += self.c

        end = (self.lc_row, self.lc_col)
        return Token(TT.NUMBER, int(number), start, end)

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

        start = (self.lc_row, self.lc_col)

        for match_char in word:
            if self.lc != match_char:
                break
            end = (self.lc_row, self.lc_col)
            self.next_char()
        else:
            if self.lc not in self.LETTER_DIGIT:
                return Token(tokentype, word, start, end)

        self.lc_row, self.lc_col, self.c, self.lc = lc_row_copy, lc_col_copy,\
            c_copy, lc_copy

    def _identifier(self):
        """identifier

        :grammar: <letter> <letter_digit>*
        :returns: None

        """
        start = (self.lc_row, self.lc_col)

        word = ""
        while self.lc in self.LETTER_DIGIT:
            word += self.lc
            self.next_char()

        end = (self.lc_row, self.lc_col)
        return Token(TT.IDENTIFIER, word, start, end)

    def _not(self, ):
        """

        :grammar: '!''='?
        :returns: None

        """
        start, end = ((self.lc_row, self.lc_col) * 2)
        self.next_char()
        if self.lc == '=':
            end = (self.lc_row, self.lc_col)
            self.next_char()
            return Token(TT.COMP_OP, '!=', start, end)
        return Token(TT.NOT, self.c, start, end)

    def _and(self):
        """

        :grammar: &&?
        :returns: None

        """
        start, end = ((self.lc_row, self.lc_col) * 2)
        self.next_char()
        if self.lc == '&':
            end = (self.lc_row, self.lc_col)
            self.next_char()
            return Token(TT.AND, "&&", start, end)
        return Token(TT.BINOP_PREC_1, self.c, start, end)

    def _or(self):
        """

        :grammar: '|''|'?
        :returns: None

        """
        start, end = ((self.lc_row, self.lc_col) * 2)
        self.next_char()
        if self.lc == '|':
            end = (self.lc_row, self.lc_col)
            self.next_char()
            return Token(TT.OR, "||", start, end)
        return Token(TT.BINOP_PREC_1, self.c, start, end)

    def _comp_operator_assignment_bitshift(self):
        """

        :grammar: ((==?)|(<(<|=)?)|(>(>|=)?))
        :returns: None
        """
        start, end = ((self.lc_row, self.lc_col) * 2)
        if self.lc == '=':
            self.next_char()
            if self.lc == '=':
                end = (self.lc_row, self.lc_col)
                self.next_char()
                return Token(TT.COMP_OP, "==", start, end)
            return Token(TT.ASSIGNMENT, '=', start, end)
        elif self.lc == '<':
            self.next_char()
            if self.lc == '=':
                end = (self.lc_row, self.lc_col)
                self.next_char()
                return Token(TT.COMP_OP, "<=", start, end)
            elif self.lc == '<':
                end = (self.lc_row, self.lc_col)
                self.next_char()
                return Token(TT.BITSHIFT, "<<", start, end)
            return Token(TT.COMP_OP, self.c, start, end)
        elif self.lc == '>':
            self.next_char()
            if self.lc == '=':
                end = (self.lc_row, self.lc_col)
                self.next_char()
                return Token(TT.COMP_OP, ">=", start, end)
            elif self.lc == '>':
                end = (self.lc_row, self.lc_col)
                self.next_char()
                return Token(TT.BITSHIFT, ">>", start, end)
            return Token(TT.COMP_OP, self.c, start, end)

    def _division_sign_or_comment(self, ):
        """

        :grammar: /(/|('*'.*'*'/))?
        :returns: None
        """
        start, end = ((self.lc_row, self.lc_col) * 2)
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
            return Token(TT.BINOP_PREC_1, self.c, start, end)
