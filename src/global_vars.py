class Args:
    def __init__(self, infile):
        self.infile = infile
        self.concrete_syntax = True
        self.tokens = True
        self.abstract_syntax = True
        self.symbol_table = True
        self.print = True
        self.begin_data_segment = 128
        self.end_data_segment = 256
        self.distance = 20
        self.verbose = True
        self.sight = 2
        self.color = True
        self.opimization_level = 0


# options from command-line arguments
args = Args("")

# for the taste method of the BacktrackingParser
is_tasting = 0

# for turning the "writing the nodetype in front of the parenthesis" for
# __repr__ temporarily on and off
show_node = True

# constants to determine whether a number is in the right range for a certain
# dataype etc.
RANGE_OF_CHAR = (-128, 127)
RANGE_OF_PARAMETER = (-2097152, 2097151)
RANGE_OF_INT = (-2147483648, 2147483647)
