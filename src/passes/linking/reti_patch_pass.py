from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error
from bitstring import Bits
import sys


class RetiPatchPass:
    # =========================================================================
    # =                               RETI_Patch                              =
    # =========================================================================
    # - deal with large immediates
    # - deal with goto directly to next block
    # - deal with division by 0
    # - what if the main fun isn't the first fun in the file
    # - what is there's no main function

    def count_instrs(self, instrs):
        cnt = 0
        for instr in instrs:
            match instr:
                case pn.SingleLineComment():
                    pass
                case rn.Jump(rn.Eq(), pn.GoTo()) if global_vars.args.no_long_jumps:
                    cnt += 5
                case rn.Jump(rn.Always(), rn.Name()) if global_vars.args.no_long_jumps:
                    cnt += 4
                case _:
                    cnt += 1
        return cnt

    def _write_large_immediate_in_register(self, reg, s_num):
        bits = Bits(int=s_num, length=32).bin
        h_bits = bits[0:22]
        l_bits = bits[22:32]
        h_num = Bits(bin=h_bits).int
        l_num = Bits(bin="0" + l_bits).int
        return self._single_line_comment(reg, "# write large immediate into") + [
            rn.Instr(rn.Loadi(), [reg, rn.Im(str(h_num))]),
            rn.Instr(rn.Multi(), [reg, rn.Im(str(2**10))]),
            rn.Instr(rn.Ori(), [reg, rn.Im(str(l_num))]),
        ]

    def _reti_patch_instr(self, instr, current_block_name, is_last_instr):
        match instr:
            # case pn.Exp(pn.GoTo(pn.Name(val))):
            case rn.Jump(rn.Always(), rn.Name(val)):
                if not is_last_instr:
                    return [instr]
                goto_block_name = val
                goto_block_idx = self.all_blocks[goto_block_name].block_idx
                current_block_idx = self.all_blocks[current_block_name].block_idx
                if current_block_idx - 1 == goto_block_idx:
                    return self._single_line_comment(instr, "# // not included")
                else:
                    return [instr]
            case rn.Instr(rn.Div(), _):
                return self._single_line_comment(
                    instr, "# check division by zero for"
                ) + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                    rn.Jump(rn.NEq(), rn.Im("3")),
                    # ACC=1 is DivisionByZero error
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
                    rn.Jump(rn.Always(), rn.Im("0")),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")]
                    ),
                    instr,
                ]
            # case rn.Instr(rn.Divi(), [_, rn.Im("0")]) doesn't occur
            case rn.Instr((rn.Loadin() | rn.Storein() | rn.Tsl()) as op, [reg1, reg2, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) or s_num > 2**31 - 1:
                    throw_error(
                        f"Immediate literal {s_num} for {type(op).__name__.upper()} "
                        "does not fit in a signed 32-bit integer"
                    )
                elif s_num < -(2**21) or s_num > 2**21 - 1:
                    # TODO: internal error if reg1 + u_num over 2^32-1
                    # the ACC register is never used as first arg of LOADIN in
                    # the compilation process
                    match op:
                        case rn.Loadin():
                            return self._write_large_immediate_in_register(
                                rn.Reg(rn.Acc()), s_num
                            ) + [
                                rn.Instr(rn.Add(), [reg1, rn.Reg(rn.Acc())]),
                                rn.Instr(rn.Loadin(), [reg1, reg2, rn.Im("0")]),
                            ]
                        case rn.Storein():
                            return self._write_large_immediate_in_register(
                                rn.Reg(rn.Acc()), s_num
                            ) + [
                                rn.Instr(rn.Add(), [reg1, rn.Reg(rn.Acc())]),
                                rn.Instr(rn.Storein(), [reg1, reg2, rn.Im("0")]),
                            ]
                        case rn.Tsl():
                            return self._write_large_immediate_in_register(
                                rn.Reg(rn.Acc()), s_num
                            ) + [
                                rn.Instr(rn.Add(), [reg1, rn.Reg(rn.Acc())]),
                                rn.Instr(rn.Tsl(), [reg1, reg2, rn.Im("0")]),
                            ]
                        case _:
                            throw_error(op)
                else:
                    return [instr]
            case rn.Instr(rn.Loadi(), [reg, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) or s_num > 2**31:
                    sys.exit(1)
                elif s_num < -(2**21) or s_num > 2**21 - 1:
                    return self._write_large_immediate_in_register(reg, s_num)
                else:
                    return [instr]
            case _:
                return [instr]

    def _reti_patch_block(self, block):
        match block:
            case pn.Block(name, instrs):
                current_block_name = name
                patched_instrs = []
                for instr in instrs:
                    patched_instrs += self._inherit_origin_many(
                        self._reti_patch_instr(
                            instr,
                            current_block_name,
                            instr == instrs[-1],
                        ),
                        instr,
                    )
                block.stmts_instrs[:] = patched_instrs
                # this has to be done in this pass, because the reti_blocks
                # pass sometimes needs to access this attribute from a block
                # where it hasn't yet beeen determined
                # TODO: Move this into the patch_instructions pass, because
                # in this pass goto(next_block_name) gets removed
                block.instrs_before = pn.Num(str(self.instrs_cnt))
                num_instrs = self.count_instrs(block.stmts_instrs)
                block.num_instrs = pn.Num(str(num_instrs))
                self.instrs_cnt += num_instrs

    def _reti_patch_section(self, section):
        match section:
            case pn.Section(_, entries):
                for entry in entries:
                    match entry:
                        case pn.Block():
                            self._reti_patch_block(entry)
                        case _:
                            # interrupt_vector_table/data entries need no patching.
                            pass
            case _:
                throw_error(section)

    def reti_patch(self, file: pn.File):
        match file:
            case pn.File(pn.Name(val), sections):
                self.instrs_cnt = 0
                for section in sections:
                    match section:
                        case pn.Section("text", _):
                            self._reti_patch_section(section)
                        case pn.Section():
                            pass
                        case pn.SingleLineComment():
                            pass
                        case _:
                            throw_error(section)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_patch"),
                    sections,
                )
            case _:
                throw_error(file)
