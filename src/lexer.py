from errors import Errors
from enum import Enum
import string
import global_vars


class Token():
    """Identifies what a certiain string slice is"""

    __match_args__ = ("type", "value")

    def __init__(self, tokentype, value, position):
        """
        :type: TT
        :value: string
        :position: (row, column) in the file where the token starts
        """
        self.type = tokentype
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
    NEG_OP = "~"
    EQ_COMP = "=="
    UEQ_COMP = "!="
    LT_COMP = "<"
    GT_COMP = ">"
    LE_COMP = "<="
    GE_COMP = ">="
    ASSIGNMENT = "="
    NOT = "!"
    AND = "&&"
    OR = "||"
    L_PAREN = "("
    R_PAREN = ")"
    L_BRACE = "{"
    R_BRACE = "}"
    CONST = "const"  # constant qualifier
    VAR = "var"  # var qualifier
    INT = "int"
    CHAR = "char"
    VOID = "void"
    NUMBER = "number"
    CHARACTER = "character"
    IDENTIFIER = "identifier"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    MAIN = "main"
    EOF = "end of file"


SPECIAL_MAPPINGS = ("&", "|", "=", "<", ">", "!")
NOT_TO_MAP = ("/", "number", "character", "identifier", "var", "to bool",
              "end of file")

STRING_TO_TT_SIMPLE = {
    value.value: value
    for value in (
        value for key, value in TT.__dict__.items()
        if not key.startswith('_') and value.value not in NOT_TO_MAP
        and value.value[0] not in SPECIAL_MAPPINGS and len(value.value) < 2)
}
STRING_TO_TT_COMPLEX = {
    value.value: value
    for value in (
        value for key, value in TT.__dict__.items()
        if not key.startswith('_') and value.value not in NOT_TO_MAP
        and value.value[0] in SPECIAL_MAPPINGS and len(value.value) <= 2)
}
STRING_TO_TT_WORDS = {
    value.value: value
    for value in (
        value for key, value in TT.__dict__.items()
        if not key.startswith('_') and value.value not in NOT_TO_MAP
        and value.value[0] not in SPECIAL_MAPPINGS and len(value.value) >= 2)
}


class Lexer:
    """Identifies tokens in the picoC code

    :Info: The Lexer doesn't check if the token is also at the right position
    to follow the grammar rules (that's the task of the parser). That's why
    12ab will be split into a number an identifier Token and it's the task of
    the Parser to raise an error. That's also the reason why self.next_char()
    is used instead of self.match()
    """

    EOF_CHAR = 'EOF'
    DIGIT_WITHOUT_ZERO = "123456789"
    DIGIT_WITH_ZERO = "0123456789"
    LETTER = string.ascii_letters
    LETTER_DIGIT = LETTER + DIGIT_WITH_ZERO

    def __init__(self, finput):
        """
        :lc: lookahead character
        :c: character
        """
        self.finput = finput
        self.lc_col = 0
        self.lc_row = 0
        self.lc = finput[self.lc_row][self.lc_col]
        self.c = ''
        # position variable to be available between methods
        self.position = (0, 0)

    def next_token(self):
        """identifies the next Token in the picoC code

        :returns: Token
        """
        while self.lc != self.EOF_CHAR:
            self.position = (self.lc_row, self.lc_col)
            if self.lc in ' \t':
                self.next_char()
            elif STRING_TO_TT_SIMPLE.get(self.lc):
                # simple symbols
                # :grammar: ;|+|-|*|%|^|~|(|)|{|}
                self.next_char()
                return Token(STRING_TO_TT_SIMPLE[self.c], self.c,
                             self.position)
            elif STRING_TO_TT_COMPLEX.get(self.lc):
                # complex symbols that are easily confusable
                # :grammar: &|&&|<bar>|<bar><bar>|!|!=|<<|>>|=|==|<
                # |>|<=|>=
                self.next_char()
                if STRING_TO_TT_COMPLEX.get(self.c + self.lc):
                    symbol = self.c + self.lc
                    self.next_char()
                    return Token(STRING_TO_TT_COMPLEX[symbol], symbol,
                                 self.position)
                return Token(STRING_TO_TT_COMPLEX[self.c], self.c,
                             self.position)
            elif self.lc in self.LETTER + '_.':
                # identifier or special keyword symbol
                # :grammar: <identifier>|if|else|while|do|int|char
                # |void|const|main
                # :identifier: <letter> <letter_digit>*
                self.next_char()
                symbol = self.c
                while self.lc in self.LETTER_DIGIT + "_./":
                    self.next_char()
                    symbol += self.c
                if STRING_TO_TT_WORDS.get(symbol):
                    return Token(STRING_TO_TT_WORDS[symbol], symbol,
                                 self.position)
                return Token(TT.IDENTIFIER, symbol, self.position)
            elif self.lc in self.DIGIT_WITH_ZERO:
                # number
                # :grammar: 0|(<digit_without_zero><digit_with_zero>*)
                if self.lc == 0:
                    self.next_char()
                    return Token(TT.NUMBER, self.c, self.position)
                # else: self.lc in self.DIGIT_WITHOUT_ZERO:
                self.next_char()
                symbol = self.c
                while self.lc in self.DIGIT_WITH_ZERO:
                    self.next_char()
                    symbol += self.c
                return Token(TT.NUMBER, symbol, self.position)
            elif self.lc == "'":
                # character
                # :grammar: '<letter_digit>'
                self.next_char()

                if self.lc not in self.LETTER_DIGIT:
                    raise Errors.InvalidCharacterError(
                        self.lc, (self.lc_row, self.lc_col))

                self.next_char()
                char = self.c

                if self.lc == "'":
                    self.next_char()
                else:
                    raise Errors.UnclosedCharacterError(
                        "'" + self.c + "'", "'" + self.c + self.lc,
                        self.position)
                return Token(TT.CHARACTER, str(ord(char)), self.position)
            elif self.lc == '/':
                # division or comments
                # :grammar: /(/|(<star>.*<start>/))?
                self.next_char()
                if self.lc == '/':
                    self.lc_col = len(self.finput[self.lc_row]) - 1
                    self.next_char()
                elif self.lc == '*':
                    while not (self.lc == '/' and self.c == '*'
                               or self.lc == self.EOF_CHAR):
                        self.next_char()
                    self.next_char()
                else:
                    return Token(TT.DIV_OP, self.c, self.position)
            else:
                raise Errors.InvalidCharacterError(self.lc, self.position)
        return Token(TT.EOF, self.lc, self.position)

    def next_char(self):
        """go to the next character, detect if "end of file" is reached

        :returns: None
        """
        # next column or next row
        if self.lc_col < len(self.finput[self.lc_row]) - 1:
            self.lc_col += 1
        elif (self.lc_col == len(self.finput[self.lc_row]) - 1
              and self.lc_row < len(self.finput) - 1):
            self.lc_row += 1
            self.lc_col = 0
        elif (self.lc_col == len(self.finput[self.lc_row]) - 1
              and self.lc_row == len(self.finput)) - 1:
            self.lc_col += 1

        # next character
        self.c = self.lc
        if (self.lc_col == len(self.finput[self.lc_row])
                and self.lc_row == len(self.finput) - 1):
            self.lc = self.EOF_CHAR
        else:
            self.lc = self.finput[self.lc_row][self.lc_col]

    def __repr__(self, ):
        return str(self.finput)
