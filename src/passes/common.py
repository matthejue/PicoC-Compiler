from src.ast_node import copy_source_origin, copy_source_origin_to_many
from src.symbol_table import SymbolTable


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
