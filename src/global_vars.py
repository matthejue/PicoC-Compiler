import reti_nodes as rn
import picoc_nodes as pn


class Args:
    def __init__(self):
        # --------------------------- PicoC_Compiler --------------------------
        self.infile = "stdin.picoc"
        # ----------------- PicoC_Compiler + RETI_Interpreter -----------------
        self.intermediate_stages = True
        self.print = True
        self.lines = 2
        self.verbose = False
        self.double_verbose = False
        self.color = True
        self.debug = False
        self.traceback = False
        self.example = False
        self.supress_errors = False
        # -------------------------- RETI_Interpreter -------------------------
        self.run = True
        self.process_begin = 3
        self.datasegment_size = 32
        self.show_mode = False
        self.pages = 5
        self.extension = "reti_states"
        self.binary = False


# options from command-line arguments
args = Args()

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
path = ""
basename = ""

reti_states = ""

uart_size = 3

is_instr = False

max_print_out_elements = 5

extension = "picoc"

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

NODE_TO_Symbol = {pn.Add: "+", pn.Sub: "-"}

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

BUILTIN_FUNS = ["print", "input"]

NEG_RELS = {
    "==": rn.NEq(),
    "!=": rn.NEq(),
    "<": rn.GtE(),
    "<=": rn.Gt(),
    ">": rn.LtE(),
    ">=": rn.Lt(),
}

IMPORTANT_STMTS_INSTRS = [
    pn.Ref,
    #  pn.Assign,
    pn.Assign(pn.Stack, pn.Global),
    pn.Assign(pn.Stack, pn.Stackframe),
    pn.Assign(pn.Global, pn.Stack),
    pn.Assign(pn.Stackframe, pn.Stack),
    pn.Assign(pn.Name, object),
    pn.Assign(pn.Attr, object),
    pn.Assign(pn.Subscr, object),
    pn.Assign(pn.Stack, pn.Stack),
    #  pn.Exp,
    pn.Exp(pn.Num),
    pn.Exp(pn.Name),
    pn.Exp(pn.BinOp),
    pn.Exp(pn.Stack),
    pn.Exp(pn.Global),
    pn.Exp(pn.Stackframe),
    pn.Exp(pn.Subscr),
    pn.Exp(pn.Attr),
    pn.Exp(pn.Deref),
    pn.Exp(pn.Ref),
    pn.Exp(pn.GoTo),
    pn.Exp(rn.Reg),
    pn.StackMalloc,
    pn.NewStackframe,
    pn.RemoveStackframe,
    pn.Return,
    pn.Exit,
    pn.If,
    pn.IfElse,
    pn.While,
    pn.DoWhile,
    pn.StackMalloc,
]
