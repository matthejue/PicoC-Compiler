from lexer import Token, TT


def _number(self):
    """number

    :grammar: <digit_without_zero> <digit_with_zero>*
    :returns: Number Token
    """
    self.next_char()
    number = self.c
    while self.lc in self.DIGIT_WITH_ZERO:
        self.next_char()
        number += self.c

    return Token(TT.NUMBER, number, self.position)


def _character(self, ):
    """character

    :grammar: "<letter_digit>*"
    :returns: None
    """
    self.next_char()
    word = ""
    while self.lc in self.LETTER_DIGIT:
        self.next_char()
        word += self.c

    self.next_char()

    return Token(TT.IDENTIFIER, word, self.position)


def _identifier_special_keyword(self):
    """

    :grammar: <identifier> | <if> | <else> | <while> | <do> | <int>
    | <char> | <void> | <const> | <main>
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
    """checks if a word matches one of the special keywords of the PicoC
    language

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
        if self.lc not in self.LETTER_DIGIT or self._reached_end_of_line():
            return Token(tokentype, word, self.position)

    self.lc_row, self.lc_col, self.c, self.lc = lc_row_copy, lc_col_copy,\
        c_copy, lc_copy


def _reached_end_of_line(self, ):
    """If one has e.g. 'if (...) ... else
    int car = 10;' as one liner, so the two words 'else' and 'int' don't
    get connected together to one word 'elseint'

    :returns: boolean
    """
    # already in a new linw
    return self.lc_col == 0


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
