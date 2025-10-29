from argparse import Namespace
import threading

# options from command-line arguments
args: Namespace

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
class ThreadState(threading.local):
    def __init__(self) -> None:
        # runs once per thread (on first access in that thread)
        self.path_without_ext: str = ""   # or Optional[str] if it can be unset

tstate = ThreadState()

reti_states = ""

uart_size = 3

next_as_22 = False

next_as_normal = False

max_print_out_elements = 5

input = []
expected = []

terminal_columns = 72
terminal_lines = 24

# constants to determine whether a number is in the right range for a certain
# dataype etc.
RANGE_OF_CHAR = (-128, 127)
RANGE_OF_PARAMETER = (-2097152, 2097151)
RANGE_OF_INT = (-2147483648, 2147483647)

TOKENNAME_TO_SYMBOL = {
    "NUM": "number",
    "CHAR": "character",
    "NAME": "identifier",
    "INT_NAME": "identifier",
    "CHAR_NAME": "identifier",
    "VOID_NAME": "identifier",
    "RETI_COMMENT": "reti comment",
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
    "MUL_DEREF_PNTR": "'*'",
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
