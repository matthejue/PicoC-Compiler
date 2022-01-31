from dataclasses import dataclass


@dataclass
class Args:
    concrete_syntax = True
    token = True
    abstract_syntax = True
    symbol_table = True
    print = True
    begin_data_segment = 128
    end_data_segment = 256
    distance = 20
    verbose = True
    sight = 2
    color = False
    opimization_level = 0


# options from command-line arguments
args = Args()

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
