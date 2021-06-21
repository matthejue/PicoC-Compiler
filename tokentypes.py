import string

###############################################################################
#                           Arithmetic expressions                            #
###############################################################################

T_CONSTANT = 'CONSTANT'
T_IDENTIFIER = 'IDENTIFIER'
T_UNOP = 'UNOP'
T_BINOP = 'BINOP'
T_SEMICOLON = 'SEMICOLON'
T_L_PAREN = 'L_PAREN'
T_R_PAREN = 'R_PAREN'
T_PRECEDENCE_1 = 'PRECEDENCE_1'
T_PRECEDENCE_2 = 'PRECEDENCE_2'
T_PRECEDENCE_3 = 'PRECEDENCE_3'
T_PRECEDENCE_4 = 'PRECEDENCE_4'
T_PRECEDENCE_5 = 'PRECEDENCE_5'
T_EOF = 'EOF'

###############################################################################
#                             Variable assignment                             #
###############################################################################

T_EQUALS = 'EQUALS'

###############################################################################
#                                   Values                                    #
###############################################################################

LETTERS = string.ascii_letters
DIGITS = "123456789"
LETTERS_DIGITS = LETTERS + DIGITS + '_'
DIGITS_WITH_ZERO = "0123456789"
BINOPS = "+-*/%&|^"
UNOPS = "-~"
OP_PRECEDENCE_1 = "*/%"
OP_PRECEDENCE_2 = "+-"
OP_PRECEDENCE_3 = "&"
OP_PRECEDENCE_4 = "^"
OP_PRECEDENCE_5 = "|"
