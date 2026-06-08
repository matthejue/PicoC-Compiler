from src.ast_node import copy_source_origin, copy_source_origin_to_many
from src import reti_nodes as rn
from src.symbol_table import SymbolTable
from bitstring import Bits


class PassStateMixin:
    def __init__(self):
        # -------------------------------- PicoC_Shrink ---------------------------------
        # Maps a string literal value to the generated global symbol name.
        # This lets identical string literals reuse the same generated array.
        self.generated_string_literals = {}
        # Holds the generated global definitions for string literals.
        # These definitions are prepended to the shrunk declarations.
        self.generated_string_defs = []
        # Counter for unique string literal names like __strlit_0.
        self.generated_string_counter = 0
        # Inline function definitions collected before shrink rewriting.
        # Shrink uses them to replace inline calls with their body/expression.
        self.inline_functions = {}

        # -------------------------------- PicoC_Blocks ---------------------------------
        # Counter for generated block labels and block ordering metadata.
        # Used for labels like if.4 and if_cont.6 and for block.block_idx.
        self.block_idx = 0
        # Maps every block label to the corresponding block node.
        # Later passes use this for jump resolution and label uniqueness.
        self.all_blocks = dict()

        # -------------------------------- PicoC_Symbol ---------------------------------
        # Symbols for globals, functions, locals, params, structs, and builtins.
        # Linking later merges per-file symbol tables into one combined table.
        self.symbol_table = SymbolTable()
        # Current symbol-table scope while rewriting/typing/lowering.
        # Usually "global" or the current function.
        self.current_scope = "global"
        # Next stack-frame address while declaring function parameters.
        # Incremented by each parameter's size.
        self.next_param_addr = 0
        # Next stack-frame address while declaring local variables.
        # After a function is processed, this is its local-frame size.
        self.next_local_addr = 0
        # Maps function names to their final local stack-slot count.
        # ANF reads this when it needs the local-frame size context.
        self.fun_local_sizes = {}
        # Rewritten top-level initialization statements.
        # The symbol pass emits these as the _global_inits block.
        self.global_decl_stmts = []
        # Maps each block label to its owning scope/function.
        # Later flat block passes use this to recover function scope.
        self.block_scopes = {}

        # ---------------------------------- PicoC_ANF ----------------------------------
        # True while lowering function-call arguments.
        # It changes how some expressions are handled while args are pushed.
        self.argmode_on = False

        # --------------------------------- RETI_Patch ----------------------------------
        # Running instruction count used to record each block's start position.
        # RETI uses those positions later to resolve symbolic jumps and labels.
        self.instrs_cnt = 0

    def _inherit_origin(self, target, source):
        return copy_source_origin(target, source)

    def _inherit_origin_many(self, targets, source):
        return copy_source_origin_to_many(targets, source)

    def _write_large_immediate_in_register(self, reg, s_num):
        if s_num < -(2**31) or s_num > 2**32 - 1:
            raise ValueError(f"{s_num} does not fit in 32 bits")

        if s_num < 0:
            bits = Bits(int=s_num, length=32).bin
        else:
            bits = Bits(uint=s_num, length=32).bin
        h_bits = bits[0:22]
        l_bits = bits[22:32]
        h_num = Bits(bin=h_bits).int
        l_num = Bits(bin="0" + l_bits).int
        return self._single_line_comment(reg, "# write large immediate into") + [
            rn.Instr(rn.Loadi(), [reg, rn.Im(str(h_num))]),
            rn.Instr(rn.Multi(), [reg, rn.Im(str(2**10))]),
            rn.Instr(rn.Ori(), [reg, rn.Im(str(l_num))]),
        ]
