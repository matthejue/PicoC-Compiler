from source import global_vars
from source import picoc_nodes as pn
from source import reti_nodes as rn
from source.utils.util_funs_dependent import throw_error


class RetiPatchPass:
    SRAM_BASE = 2**31
    SIGNED_22_MIN = -(2**21)
    SIGNED_22_MAX = 2**21 - 1
    SIGNED_32_MIN = -(2**31)
    SIGNED_32_MAX = 2**31 - 1

    def _jump32_size(self, rel, target):
        match target:
            case rn.Im():
                target_size = 4
            case rn.Name() | rn.BinOp():
                target_size = 5
            case _:
                throw_error(f"Unsupported JUMP32 target: {target}")

        return target_size + (0 if isinstance(rel, rn.Always) else 1)

    def count_instrs(self, instrs):
        cnt = 0
        for instr in instrs:
            match instr:
                case pn.SingleLineComment():
                    pass
                # Immediate LOADI32/JUMP32 only come from user-written .reti_blocks.
                # The PicoC compilation pipeline emits symbolic targets instead.
                case rn.Jump32(rel, target):
                    cnt += self._jump32_size(rel, target)
                case rn.Instr(rn.Loadi32(), _):
                    cnt += 3
                case rn.Instr((rn.Push() | rn.Pop()), _):
                    cnt += 2
                # The compiler pipeline only emits JUMP32/LOADI32 for symbolic
                # addresses. Plain symbolic operands may still come from
                # user-written .reti_blocks, but they stay short and are not
                # always working: if the final address needs more than 22 bits,
                # later stages intentionally produce incorrect code instead of
                # expanding them.
                case _:
                    cnt += 1
        return cnt

    def _resolve_immediate_ivte(self, val):
        return rn.Im(str(self.SRAM_BASE + int(val)))

    def _next_emitted_block_name(self, entries, start_idx):
        for entry in entries[start_idx + 1 :]:
            match entry:
                case pn.SingleLineComment():
                    continue
                case pn.Block(name, _):
                    return name
                case _:
                    return None
        return None

    def _reti_patch_instr(self, instr, next_block_name, is_last_instr):
        match instr:
            # Example: IVTE 5 writes the SRAM address 2^31 + 5.
            case rn.Ivte(rn.Im(val)):
                return [self._resolve_immediate_ivte(val)]
            # Only unconditional jumps can be omitted when their target is the
            # next emitted block; conditional jumps still encode a branch decision.
            # PicoC emits JUMP32, but user-written .reti_blocks or asm()
            # can also introduce short symbolic JUMP directly.
            # Example: JUMP32 next_block or JUMP next_block at block end.
            case rn.Jump32(rn.Always(), rn.Name(target_block_name)) | rn.Jump(
                rn.Always(), rn.Name(target_block_name)
            ):
                if target_block_name not in self.all_blocks:
                    jump_kind = "JUMP32" if isinstance(instr, rn.Jump32) else "JUMP"
                    throw_error(f"Unknown block target for {jump_kind}: {target_block_name}")
                if not is_last_instr:
                    return [instr]

                # Remove an unnecessary jump to the next emitted block.
                if target_block_name == next_block_name:
                    return self._single_line_comment(instr, "# // not included")
                return [instr]
            # Expand stack pseudo instructions while blocks still exist, so
            # block sizes include their real machine-instruction length.
            case rn.Instr(rn.Push(), [rn.Reg() as reg]):
                return [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(rn.Storein(), [rn.Reg(rn.Sp()), reg, rn.Im("1")]),
                ]
            case rn.Instr(rn.Pop(), [rn.Reg() as reg]):
                return [
                    rn.Instr(rn.Loadin(), [rn.Reg(rn.Sp()), reg, rn.Im("1")]),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
            # Example: a large LOADIN offset is added to the base register first,
            # then the same memory op is emitted with offset 0.
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

    def _reti_patch_block(self, block, next_block_name, section_name, section_start):
        match block:
            case pn.Block(_, instrs):
                patched_instrs = []
                for instr_idx, instr in enumerate(instrs):
                    patched_instrs += self._inherit_origin_many(
                        self._reti_patch_instr(
                            instr,
                            next_block_name,
                            instr_idx == len(instrs) - 1,
                        ),
                        instr,
                    )
                block.stmts_instrs[:] = patched_instrs
                block.section_name = section_name
                block.section_start = pn.Num(str(section_start))
                block.instrs_before = pn.Num(str(self.instrs_cnt - section_start))
                num_instrs = self.count_instrs(block.stmts_instrs)
                block.num_instrs = pn.Num(str(num_instrs))
                self.instrs_cnt += num_instrs

    def _reti_patch_section(self, section):
        match section:
            case pn.Section(section_name, entries):
                section_start = self.instrs_cnt
                patched_entries = []
                for entry_idx, entry in enumerate(entries):
                    match entry:
                        case pn.Block():
                            self._reti_patch_block(
                                entry,
                                self._next_emitted_block_name(entries, entry_idx),
                                section_name,
                                section_start,
                            )
                            patched_entries.append(entry)
                        case _:
                            patched = self._inherit_origin_many(
                                self._reti_patch_instr(entry, None, False),
                                entry,
                            )
                            patched_entries += patched
                            self.instrs_cnt += self.count_instrs(patched)
                entries[:] = patched_entries
            case _:
                throw_error(section)

    def reti_patch(self, file: pn.File):
        match file:
            case pn.File(pn.Name(val), sections):
                self.instrs_cnt = 0
                for section in sections:
                    match section:
                        case pn.Section(_, _):
                            self._reti_patch_section(section)
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
