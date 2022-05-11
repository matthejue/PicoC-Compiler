from picoc_nodes import N as PN
from reti_nodes import N as RN


class PicoCCompiler:
    def __init__(self):
        self.block_id = 0
        self.stmt_cnt = 0

    def picoc_to_picoc_mon_def(self):
        pass

    def _picoc_to_picoc_mon(self):
        pass

    # =========================================================================
    # =                       PicoC_mon -> PicoC_Blocks                       =
    # =========================================================================

    def _create_block(self, name, stmts, blocks):
        blockname = f"{name}.{self.block_id}"
        new_block = PN.Block(blockname, stmts, PN.Num(str(self.stmt_cnt)))
        blocks[blockname] = new_block
        self.stmt_cnt += len(stmts)
        self.block_id += 1
        return PN.GoTo(PN.Name(blockname))

    def _picoc_mon_to_picoc_block_condition_if(
        self, condition, stmts_if, stmts_else, blocks
    ):
        pass

    def _picoc_mon_to_picoc_block_condition_if_else(
        self, condition, stmts_if, stmts_else, blocks
    ):
        match condition:
            case PN.Atom():
                goto_if = self._create_block("if", stmts_if, blocks)
                goto_else = self._create_block("else", stmts_else, blocks)
                return PN.IfElse(condition, [goto_if], [goto_else])

    def _picoc_mon_to_picoc_block_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            case PN.Exp(PN.Call(name, exps)):
                pass
            case PN.Alloc(type_qual, size_qual, pntr_decl):
                pass
            case PN.Assign(location, logic_exp):
                return
            case PN.If(condition, stmts):
                pass
            case PN.IfElse(condition, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )
                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_if, blocks
                    )
                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_else, blocks
                    )
                return self._picoc_mon_to_picoc_block_condition_if_else(
                    condition, stmts_if, stmts_else, blocks
                )
            case PN.While():
                pass
            case PN.DoWhile():
                pass
            case PN.Return():
                pass
        return PN.Block()

    def _picoc_mon_to_picoc_block_def(self, fun):
        match fun:
            case PN.FunDef(size_qual, fun_name, params, stmts):
                blocks = dict()
                processed_stmts = []
                fun_block = self._create_block(fun_name, processed_stmts, blocks)
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_mon_to_picoc_block_stmt(
                        stmt, processed_stmts, blocks
                    )
                return PN.FunDef(size_qual, fun_name, params, fun_block + blocks)

    def picoc_mon_to_picoc_block(self, file):
        funs_with_blocks = []
        match file:
            case PN.File(name, funs):
                for fun in funs:
                    funs_with_blocks += [self._picoc_mon_to_picoc_block_def(fun)]
        return PN.File(name, funs_with_blocks)

    # =========================================================================
    # =                      PicoC_Blocks -> RETI_Blocks                      =
    # =========================================================================

    def picoc_block_to_reti_block(self):
        ...

    def reti_block_to_reti(self):
        ...
