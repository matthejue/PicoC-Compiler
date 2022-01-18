# options from command-line arguments
args = None

# for the taste method of the BacktrackingParser
is_tasting = 0

# for a assignment, so that the expression on the right side knows the context
# in which it's assigned
from symbol_table import Symbol

variable_context: Symbol = None

# for turning the "writing the nodetype in front of the parenthesis" for
# __repr__ temporarily on and off
show_node = True
