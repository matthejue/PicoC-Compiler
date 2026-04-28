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
