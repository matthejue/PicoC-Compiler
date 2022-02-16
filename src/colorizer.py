from enum import Enum
from string import ascii_letters
from colormanager import ColorManager as CM
import re


class Colorizer:
    EOF_CHAR = 'EOF'

    class States(Enum):
        # to reti code
        COMMAND = 0
        SPACE = 1
        PARAMETER = 2
        REGISTER = 3
        SEMICOLON = 4
        COMMENT = 5
        # for symbol table
        TABLE = 6
        HEADING = 7
        WORD_CELL = 8
        NUMBER_CELL = 9
        # for abstract syntax
        PARENTHESIS = 10
        OPERATOR = 11
        NUMBER = 12
        WORD = 13
        # for tokens
        STRUCTURE = 14
        TOKEN = 15
        TOKENTYPE = 16
        STRING = 17
        POSITION = 18
        # for help_page
        EMPHASIZED = 19
        EMPHASIZED_CONTENT = 20
        EMPHASIZED_END = 21
        TEXT = 22
        CLI_OPTION = 23
        CLI_ARGUMENT = 24
        OPTIONAL = 25

    def __init__(self, cinput):
        """
        :lc: lookahead character
        :c: character
        """
        self.cinput = cinput
        self.idx = 0
        self.c = cinput[self.idx]

        # position variable to be available between methods
        self.state = None

        # so that the color ansi escape sequence won't get inserted several times
        self.color_not_inserted = True

    def colorize_reti_code(self, ):
        self.state = self.States.COMMAND
        while self.c != self.EOF_CHAR:
            if self.c == ' ' and self.state != self.States.COMMENT:
                self.state = self.States.SPACE
                self.color_not_inserted = True
            elif (self.c in ascii_letters + '_'
                  and self.state == self.States.SPACE
                  and self.state != self.States.COMMENT):
                self.state = self.States.REGISTER
                self.color_not_inserted = True
            elif (self.c in '-1234567890' and self.state == self.States.SPACE
                  and self.state != self.States.COMMENT):
                self.state = self.States.PARAMETER
                self.color_not_inserted = True
            elif self.c == ';':
                self.state = self.States.SEMICOLON
                self.color_not_inserted = True
            elif self.c == '#':
                self.state = self.States.COMMENT
                self.color_not_inserted = True
            elif self.c == '\n':
                self.state = self.States.COMMAND
                self.color_not_inserted = True

            if self.state == self.States.COMMAND and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.REGISTER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.PARAMETER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.SEMICOLON and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.COMMENT and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().MAGENTA)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_symbol_table(self, ):
        self.state = self.States.HEADING
        while self.c != self.EOF_CHAR:
            if (self.c in ascii_letters + '_' and self.state
                    in [self.States.TABLE, self.States.NUMBER_CELL]):
                self.state = self.States.WORD_CELL
                self.color_not_inserted = True
            elif (self.c in '1234567890'
                  and self.state != self.States.WORD_CELL):
                self.state = self.States.NUMBER_CELL
                self.color_not_inserted = True
            elif self.c in '-/' and self.state in [
                    self.States.HEADING, self.States.WORD_CELL
            ]:
                self.state = self.States.TABLE
                self.color_not_inserted = True
            elif self.c in '(),':
                self.state = self.States.TABLE
                self.color_not_inserted = True

            if self.state == self.States.HEADING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.WORD_CELL and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.NUMBER_CELL and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TABLE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_abstract_syntax(self, ):
        self.state = self.States.PARENTHESIS
        while self.c != self.EOF_CHAR:
            if (self.c in ascii_letters + '_' and self.state
                    in [self.States.PARENTHESIS, self.States.OPERATOR]):
                self.state = self.States.WORD
                self.color_not_inserted = True
            elif self.c in '1234567890' and self.state != self.States.WORD:
                self.state = self.States.NUMBER
                self.color_not_inserted = True
            elif self.c in '()':
                self.state = self.States.PARENTHESIS
                self.color_not_inserted = True
            elif self.c in '+~-*%/&|!^<>=' and self.state != self.States.OPERATOR:
                self.state = self.States.OPERATOR
                self.color_not_inserted = True

            if self.state == self.States.WORD and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            if self.state == self.States.NUMBER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.PARENTHESIS and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.OPERATOR and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_tokens(self, ):
        self.state = self.States.STRUCTURE
        while self.c != self.EOF_CHAR:
            if self.c in '()[],':
                self.state = self.States.STRUCTURE
                self.color_not_inserted = True
            elif self.c in '<>':
                self.state = self.States.TOKEN
                self.color_not_inserted = True
            elif self.c == 'T' and self.state == self.States.TOKEN:
                self.state = self.States.TOKENTYPE
                self.color_not_inserted = True
            elif self.c in "'":
                self.state = self.States.STRING
                self.color_not_inserted = True
            elif (self.c in "1234567890"
                  and self.state == self.States.STRUCTURE):
                self.state = self.States.POSITION
                self.color_not_inserted = True

            if self.state == self.States.STRUCTURE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TOKEN and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().MAGENTA)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TOKENTYPE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.STRING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.POSITION and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_conrete_syntax(self, ):
        self.state = self.States.STRUCTURE
        while self.c != self.EOF_CHAR:
            if self.c in '[],':
                self.state = self.States.STRUCTURE
                self.color_not_inserted = True
            elif self.c in "\"'":
                self.state = self.States.STRING
                self.color_not_inserted = True

            if self.state == self.States.STRUCTURE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.STRING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    #  def colorize_help_page(self, ):
    #      self.state = self.States.TEXT
    #      while self.c != self.EOF_CHAR:
    #          if self.c == '=' and self.state not in [
    #                  self.States.HEADING, self.States.EMPHASIZED,
    #                  self.States.EMPHASIZED_CONTENT
    #          ]:
    #              self.state = self.States.HEADING
    #              self.color_not_inserted = True
    #          elif self.c == "`" and self.state not in [
    #                  self.States.EMPHASIZED_CONTENT, self.States.EMPHASIZED_END
    #          ]:
    #              self.state = self.States.EMPHASIZED
    #              self.color_not_inserted = True
    #          elif self.c in ascii_letters + ' =<>/!&|~*;.-^' and self.state in [
    #                  self.States.EMPHASIZED, self.States.EMPHASIZED_CONTENT
    #          ]:
    #              self.state = self.States.EMPHASIZED_CONTENT
    #              self.color_not_inserted = True
    #          elif self.c == "`" and self.state == self.States.EMPHASIZED_CONTENT:
    #              self.state = self.States.EMPHASIZED_END
    #              self.color_not_inserted = True
    #          elif self.c in ascii_letters + ' .,)' and self.state not in [
    #                  self.States.TEXT, self.States.CLI_OPTION,
    #                  self.States.CLI_ARGUMENT
    #          ]:
    #              self.state = self.States.TEXT
    #              self.color_not_inserted = True
    #          elif self.c in '-' and self.state != self.States.CLI_OPTION:
    #              self.state = self.States.CLI_OPTION
    #              self.color_not_inserted = True
    #          elif self.c in ascii_letters and self.state == self.States.CLI_OPTION:
    #              self.state = self.States.CLI_OPTION
    #              self.color_not_inserted = True
    #          elif self.c == ' ' and self.state == self.States.CLI_OPTION:
    #              self.state = self.States.CLI_ARGUMENT
    #              self.color_not_inserted = True
    #          elif self.c in ascii_letters and self.state == self.States.CLI_ARGUMENT:
    #              self.state = self.States.CLI_ARGUMENT
    #              self.color_not_inserted = True
    #          elif self.c == ' ' and self.state == self.States.CLI_ARGUMENT:
    #              self.state = self.States.TEXT
    #              self.color_not_inserted = True
    #          elif self.c == '\n':
    #              self.state = self.States.TEXT
    #              self.color_not_inserted = True
    #          elif self.c in "[]":
    #              self.state = self.States.OPTIONAL
    #              self.color_not_inserted = True
    #
    #          if self.state == self.States.EMPHASIZED and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().RED + CM().BRIGHT)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.EMPHASIZED_CONTENT and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().RED + CM().BRIGHT)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.EMPHASIZED_END and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().RED + CM().BRIGHT)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.HEADING and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().WHITE + CM().BRIGHT)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.TEXT and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().BLUE + CM().NORMAL)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.CLI_OPTION and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().GREEN + CM().NORMAL)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.CLI_ARGUMENT and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().YELLOW + CM().NORMAL)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          elif self.state == self.States.OPTIONAL and self.color_not_inserted:
    #              self.insert_colorcode(self.idx, CM().MAGENTA + CM().NORMAL)
    #              self.color_not_inserted = False
    #              self.next_char()
    #          else:
    #              self.next_char()
    #      return self.cinput + CM().RESET

    def insert_colorcode(self, idx, color):
        self.cinput = self.cinput[:idx] + color + self.cinput[idx:]
        self.idx += len(color)

    def next_char(self):
        """go to the next character, detect if "end of file" is reached

        :returns: None
        """
        # next index
        self.idx += 1

        # next character
        if self.idx == len(self.cinput):
            self.c = self.EOF_CHAR
        else:
            self.c = self.cinput[self.idx]


def colorize_help_page(cinput):
    cinput = colorize(r'(\[|\])', cinput, CM().MAGENTA, CM().BLUE)
    cinput = colorize('`[^`]+`', cinput, CM().RED, CM().BLUE)
    cinput = colorize('<.+>`', cinput, CM().RED, CM().BLUE)
    cinput = colorize('=+[^`][^`]', cinput,
                      CM().BRIGHT + CM().WHITE,
                      CM().NORMAL + CM().BLUE)
    cinput = colorize(r'[A-Z_]{2,}', cinput,
                      CM().YELLOW,
                      CM().BLUE, r'-{1,2}\w+ [A-Z_]{2,}')
    cinput = colorize(r'-{1,2}\w+', cinput, CM().GREEN, CM().BLUE)
    return CM().BLUE + cinput + CM().RESET_ALL


def colorize(pattern, cinput, ansi, default_ansi, condition=None):
    p = re.compile(condition if condition else pattern)
    num_extra_letters = 0
    itertr = p.finditer(cinput)
    for span in map(lambda i: i.span(), itertr):
        if condition:
            match_pre = re.search(
                pattern, cinput[span[0] + num_extra_letters:span[1] +
                                num_extra_letters])
            if match_pre:
                sub_span_pre = match_pre.span()
                sub_span = (span[0] + sub_span_pre[0],
                            span[0] + sub_span_pre[1])
                cinput = cinput[:sub_span[0] + num_extra_letters] + ansi + \
                    cinput[sub_span[0] +
                           num_extra_letters:sub_span[1] + num_extra_letters] +\
                    default_ansi + cinput[sub_span[1] + num_extra_letters:]
        else:
            cinput = cinput[:span[0] + num_extra_letters] + ansi + \
                cinput[span[0] + num_extra_letters:span[1] + num_extra_letters] +\
                default_ansi + cinput[span[1] + num_extra_letters:]
        num_extra_letters += len(ansi) + len(default_ansi)
    return cinput
