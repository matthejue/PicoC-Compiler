from picoc_nodes import N as PN
from reti_nodes import N as RN
import operator


class Passes:
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

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = PN.Block(PN.Name(label), stmts, PN.Num(str(self.stmt_cnt)))
        blocks[label] = new_block
        self.stmt_cnt += len(stmts)
        self.block_id += 1
        return PN.GoTo(PN.Name(label))

    def _picoc_mon_to_picoc_block_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            case PN.If(condition, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.If(condition, [goto_if])]
            case PN.IfElse(condition, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_else, blocks
                    )
                goto_else = self._create_block("else", stmts_else, blocks)

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.IfElse(condition, [goto_if], [goto_else])]
            case PN.While(condition, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                goto_condition_check = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.label.value = self._create_block(
                    "while_branch", stmts_while, blocks
                ).label.value

                condition_check = [PN.IfElse(condition, goto_branch, goto_after)]
                goto_condition_check.label.value = self._create_block(
                    "condition_check", condition_check, blocks
                ).label.value

                return [goto_condition_check]
            case PN.DoWhile(condition, stmts):
                goto_after = self._create_block(
                    "do_while_after", processed_stmts, blocks
                )

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [PN.IfElse(condition, goto_branch, goto_after)]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.label.value = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).label.value

                return [goto_branch]
            case PN.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_mon_to_picoc_block_def(self, fun):
        match fun:
            case PN.FunDef(size_qual, PN.Name(fun_name), params, stmts):
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_mon_to_picoc_block_stmt(
                        stmt, processed_stmts, blocks
                    )
                self._create_block(fun_name, processed_stmts, blocks)
                return PN.FunDef(
                    size_qual,
                    PN.Name(fun_name),
                    params,
                    list(
                        sorted(
                            blocks.values(),
                            key=lambda block: -int(
                                block.label.value[block.label.value.rindex(".") + 1 :]
                            ),
                        )
                    ),
                )

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
