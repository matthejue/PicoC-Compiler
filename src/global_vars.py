class Args:
    def __init__(self):
        # assigned in the do_most_used function because the filename has to be
        # put at the beginning of the code
        self.infile = "stdin"
        self.intermediate_stages = True
        self.print = True
        self.gap = 20
        self.lines = 2
        self.show_error_message = False
        self.verbose = False
        self.color = True
        self.debug = False


# options from command-line arguments
args = Args()

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
path = ""
basename = ""

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
