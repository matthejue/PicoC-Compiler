class Args:
    def __init__(self):
        # assigned in the do_most_used function because the filename has to be
        # put at the beginning of the code
        self.infile = "stdin"
        self.concrete_syntax = True
        self.tokens = True
        self.abstract_syntax = True
        self.symbol_table = True
        self.print = True
        self.distance = 20
        self.sight = 2
        self.color = True
        self.verbose = False
        self.debug = False
        self.show_error_message = False


# options from command-line arguments
args = Args()

# for the taste method of the BacktrackingParser
is_tasting = 0

# for turning the "writing the nodetype in front of the parenthesis" for
# __repr__ temporarily on and off
show_node = True

# Name and path for the basename of all output files. If it stays empty this
# means one is in shell mode
outbase = ""

# constants to determine whether a number is in the right range for a certain
# dataype etc.
RANGE_OF_CHAR = (-128, 127)
RANGE_OF_PARAMETER = (-2097152, 2097151)
RANGE_OF_INT = (-2147483648, 2147483647)
