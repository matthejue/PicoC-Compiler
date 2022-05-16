class Args:
    def __init__(self):
        # assigned in the do_most_used function because the filename has to be
        # put at the beginning of the code
        self.infile = "stdin"
        self.code = True
        self.tokens = True
        self.derivation_tree = True
        self.derivation_tree_simplified = True
        self.abstract_syntax_tree = True
        self.picoc_to_picoc_mon = True
        self.picoc_mon_to_picoc_blocks = True
        self.picoc_blocks_to_reti_blocks = True
        self.reti_blocks_to_reti = True
        self.symbol_table = True
        self.print = True
        self.gap = 20
        self.sight = 2
        self.color = True
        self.verbose = False
        self.debug = False
        self.show_error_message = False


# options from command-line arguments
args = Args()

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
outbase = ""

# constants to determine whether a number is in the right range for a certain
# dataype etc.
RANGE_OF_CHAR = (-128, 127)
RANGE_OF_PARAMETER = (-2097152, 2097151)
RANGE_OF_INT = (-2147483648, 2147483647)
