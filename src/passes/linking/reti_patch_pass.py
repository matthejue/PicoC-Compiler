from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error
from bitstring import Bits


class RetiPatchPass:
    SIGNED_22_MIN = -(2**21)
    SIGNED_22_MAX = 2**21 - 1
    SIGNED_32_MIN = -(2**31)
    SIGNED_32_MAX = 2**31 - 1

    def count_instrs(self, instrs):
        cnt = 0
        for instr in instrs:
            match instr:
                case pn.SingleLineComment():
                    pass
                case rn.Jump(rn.Eq(), rn.Name()) if global_vars.args.no_long_jumps:
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
            # Example: JUMPALWAYS next_block at block end can be omitted.
            case rn.Jump(rn.Always(), rn.Name(target_block_name)):
                if not is_last_instr:
                    return [instr]

                current_block = self.all_blocks[current_block_name]
                target_block = self.all_blocks[target_block_name]
                # Remove an unnecessary jump to the next emitted block.
                target_is_next_block = current_block.block_idx - 1 == target_block.block_idx

                if target_is_next_block:
                    return self._single_line_comment(instr, "# // not included")
                return [instr]
            # Example: LOADIN SP ACC 3000000 writes 3000000 to ACC, then ADD SP ACC; LOADIN SP ACC 0.
            case rn.Instr((rn.Loadin() | rn.Storein() | rn.Tsl()) as op, [base_reg, value_reg, rn.Im(val)]):
                offset = int(val)
                if offset < self.SIGNED_32_MIN or offset > self.SIGNED_32_MAX:
                    throw_error(
                        f"Immediate literal {offset} for {type(op).__name__.upper()} "
                        "does not fit in a signed 32-bit integer"
                    )

                if self.SIGNED_22_MIN <= offset <= self.SIGNED_22_MAX:
                    return [instr]

                # Large memory offsets are added to the base register first.
                scratch_reg = rn.Reg(rn.Acc())
                return self._write_large_immediate_in_register(scratch_reg, offset) + [
                    rn.Instr(rn.Add(), [base_reg, scratch_reg]),
                    rn.Instr(op, [base_reg, value_reg, rn.Im("0")]),
                ]
            # Example: LOADI ACC 3000000 writes 3000000 to ACC with LOADI/MULTI/ORI.
            case rn.Instr(rn.Loadi(), [reg, rn.Im(val)]):
                immediate = int(val)
                if immediate < self.SIGNED_32_MIN or immediate > self.SIGNED_32_MAX:
                    throw_error(
                        f"Immediate literal {immediate} for LOADI "
                        "does not fit in a signed 32-bit integer"
                    )

                if self.SIGNED_22_MIN <= immediate <= self.SIGNED_22_MAX:
                    return [instr]

                # LOADI encodes only 22-bit immediates; synthesize larger values.
                return self._write_large_immediate_in_register(reg, immediate)
            # Example: ADD ACC IN1 already needs no patching.
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
