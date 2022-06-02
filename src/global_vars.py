import reti_nodes as rn


class Args:
    def __init__(self):
        # --------------------------- PicoC_Compiler --------------------------
        self.infile = "stdin"
        # ----------------- PicoC_Compiler + RETI_Interpreter -----------------
        self.intermediate_stages = True
        self.print = True
        self.lines = 2
        self.verbose = False
        self.double_verbose = False
        self.color = True
        self.debug = False
        # -------------------------- RETI_Interpreter -------------------------
        self.run = True
        self.process_begin = 8
        self.datasegment_size = 32
        self.uart_size = 4
        self.sram_size = 0


# options from command-line arguments
args = Args()

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
path = ""
basename = ""

# eprom_size is fixed as the start program has a certain size
eprom_size = 0

# constants to determine whether a number is in the right range for a certain
# dataype etc.
RANGE_OF_CHAR = (-128, 127)
RANGE_OF_PARAMETER = (-2097152, 2097151)
RANGE_OF_INT = (-2147483648, 2147483647)

MAP_NAME_TO_SYMBOL = {
    "NUM": "number",
    "CHAR": "character",
    "NAME": "identifier",
    "INT_NAME": "identifier",
    "CHAR_NAME": "identifier",
    "VOID_NAME": "identifier",
    "NEG": "'~'",
    "NOT": "'!'",
    "SUB_MINUS": "'-'",
    "ADD": "'+'",
    "MUL": "'*'",
    "DIV": "'/'",
    "MOD": "'%'",
    "OPLUS": "'^'",
    "AND": "'&'",
    "OR": "'|'",
    "EQ": "'=='",
    "NEQ": "'!='",
    "LT": "'<'",
    "LTE": "'<='",
    "GT": "'>'",
    "GTE": "'>='",
    "INT_DT": "'int'",
    "CHAR_DT": "'char'",
    "VOID_DT": "'void'",
    "CONST": "'const'",
    "PRINT": "'print'",
    "INPUT": "'input'",
    "STRUCT": "'struct'",
    "IF": "'if'",
    "ELSE": "'else'",
    "WHILE": "'while'",
    "DO": "'do'",
    "RETURN": "'return'",
    # tokennames from https://github.com/lark-parser/lark/blob/86c8ad41c9e5380e
    # 30f3b63b894ec0b3cb21a20a/lark/load_grammar.py#L34
    "EQUAL": "'='",
    "DOT": "'.'",
    "COMMA": "','",
    "SEMICOLON": "';'",
    "STAR": "'*'",
    "LPAR": "'('",
    "RPAR": "')'",
    "LBRACE": "'{'",
    "RBRACE": "'}'",
    "LSQB": "'['",
    "RSQB": "']'",
}

MAX_PRINT_OUT_TOKENS = 5

COMPUTE_INSTRUCTION = [
    rn.Add,
    rn.Sub,
    rn.Mult,
    rn.Div,
    rn.Mod,
    rn.Oplus,
    rn.Or,
    rn.And,
]

COMPUTE_IMMEDIATE_INSTRUCTION = [
    rn.Addi,
    rn.Subi,
    rn.Multi,
    rn.Divi,
    rn.Modi,
    rn.Oplusi,
    rn.Ori,
    rn.Andi,
]
