from src.ast_node import copy_source_origin, copy_source_origin_to_many
from src import reti_nodes as rn
from src.symbol_table import SymbolTable
from bitstring import Bits


class PassStateMixin:
    def __init__(self):
        # PicoC_Blocks
        self.block_idx = 0
        self.all_blocks = dict()
        # PicoC_ANF
        self.argmode_on = False
        self.symbol_table = SymbolTable()
        self.current_scope = "global"
        self.global_stmts_instrs = []
        self.next_param_addr = 0
        self.next_local_addr = 0
        self.stack_type_hints = {}
        self.fun_local_sizes = {}
        self.global_decl_stmts = []
        self.block_scopes = {}

        self.generated_string_literals = {}
        self.generated_string_defs = []
        self.generated_string_counter = 0
        self.inline_functions = {}

        # RETI_Blocks
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
