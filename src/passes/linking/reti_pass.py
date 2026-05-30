from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error


class RetiPass:
    def _negated_rel(self, rel):
        match rel:
            case rn.Always():
                return rn.Always()
            case rn.Eq():
                return rn.NEq()
            case rn.NEq():
                return rn.Eq()
            case rn.Lt():
                return rn.GtE()
            case rn.LtE():
                return rn.Gt()
            case rn.Gt():
                return rn.LtE()
            case rn.GtE():
                return rn.Lt()
            case _:
                throw_error(rel)

    def _patch_too_large_jumps(self, rel, distance, instr):
        # Long jumps are patched here, not in reti_patch, because the concrete
        # distance is known only while flattening symbolic block targets.
        if global_vars.args.no_long_jumps:
            #  if (
            #  distance < -(2**21) and distance > 2**21 - 1
            #  ) or global_vars.args.no_jump:
            neg_rel = self._negated_rel(rel)
            instrs_for_immediate = self._write_large_immediate_in_register(
                rn.Reg(rn.Acc()), distance
            )
            return self._single_line_comment(instr, "#") + (
                ([rn.Jump(neg_rel, rn.Im("5"))] if str(rel) else [])
                + instrs_for_immediate
                + [rn.Instr(rn.Add(), [rn.Reg(rn.Pc()), rn.Reg(rn.Acc())])]
            )
        else:
            return self._single_line_comment(instr, "#") + [
                rn.Jump(rel, rn.Im(str(distance)))
            ]

    def _is_function_label(self, name):
        symbol, _ = self.symbol_table.resolve(name, scope="global")
        return isinstance(symbol, dict) and isinstance(symbol.get("datatype"), pn.FunDecl)

    def _determine_distance(self, current_block, other_block, idx):
        if int(other_block.instrs_before.val) != int(current_block.instrs_before.val):
            return (
                int(other_block.instrs_before.val)
                - int(current_block.instrs_before.val)
                - idx
            )
        else:  # int(other_block.instrs_before.val) == int(current_block.instrs_before.val):
            return -idx

    def _symbol_addr(self, var_name):
        symbol, _ = self.symbol_table.resolve(var_name, scope=self.current_scope)
        match symbol:
            case {
                "type_qual": _,
                "datatype": _,
                "name": _,
                "addr": addr,
                "size": _,
            }:
                return addr
            case _:
                throw_error(symbol)

    def _patch_named_jump(self, rel, target_name, instr, idx, current_block, idx_offset):
        target_block = self.all_blocks[target_name]
        distance_idx = idx + idx_offset if global_vars.args.no_long_jumps else idx
        distance = self._determine_distance(current_block, target_block, distance_idx)
        instrs = self._patch_too_large_jumps(rel, distance, instr)
        return instrs, distance_idx + 1

    def _reti_instr(self, instr, idx, current_block):
        match instr:
            # Resolve the target name to determine the relative jump distance.
            case rn.Jump(rn.Always(), rn.Name(target_name)):
                return self._patch_named_jump(
                    rn.Always(), target_name, instr, idx, current_block, 3
                )
            # Same as above, but conditional long jumps add a guard jump.
            case rn.Jump(rn.Eq() as rel, rn.Name(target_name)):
                return self._patch_named_jump(
                    rel, target_name, instr, idx, current_block, 4
                )
            # Resolve symbolic indexed-memory offsets, e.g. LOADIN DS ACC var_name.
            # TSL is not emitted by normal PicoC compilation, but can appear in
            # external .reti_blocks input.
            case rn.Instr(
                (rn.Loadin() | rn.Storein() | rn.Tsl()),
                [_, _, rn.Name(var_name)],
            ):
                instr.args[2] = rn.Im(self._symbol_addr(var_name))
                return [instr], idx + 1
            # Resolve symbolic indexed-memory offsets, e.g. STOREIN DS ACC var_name + 1.
            # Same TSL comment as above.
            case rn.Instr(
                (rn.Loadin() | rn.Storein() | rn.Tsl()),
                [_, _, rn.BinOp(rn.Name(var_name), op, num)],
            ):
                addr = self._symbol_addr(var_name)
                match op:
                    case rn.Add():
                        instr.args[2] = rn.Im(addr + num)
                    case rn.Sub():
                        instr.args[2] = rn.Im(addr - num)
                    case _:
                        throw_error(op)
                return [instr], idx + 1
            # Replace _this_instruction + n with the current absolute instruction address + n.
            case rn.Instr(
                rn.Loadi(),
                [
                    rn.Reg(rn.Acc()) as reg,
                    rn.BinOp(rn.Name("_this_instruction"), rn.Add(), constant),
                ],
            ):
                rel_addr = str(int(current_block.instrs_before.val) + idx + constant)
                instrs = self._single_line_comment(instr, "#") + [
                    rn.Instr(rn.Loadi(), [reg, rn.Im(rel_addr)])
                ]
                return instrs, idx + 1
            # Resolve a LOADI target name to a function or variable address from the symbol table.
            case rn.Instr(rn.Loadi(), [_, rn.Name(name)]):
                if self._is_function_label(name):
                    instr.args[1] = rn.Im(self.all_blocks[name].instrs_before.val)
                    return [instr], idx + 1

                instr.args[1] = rn.Im(self._symbol_addr(name))
                return [instr], idx + 1
            # Keep comments in output without increasing the instruction index.
            case pn.SingleLineComment():
                return [instr], idx
            # Already concrete RETI instructions pass through unchanged.
            case _:
                return [instr], idx + 1

    def _flatten_text_blocks(self, entries):
        instrs_block_free = []
        for entry in entries:
            match entry:
                case pn.Block(label, instrs) as block:
                    idx = 0
                    instrs_block_free += self._single_line_comment(
                        pn.Block(label, []), "# //"
                    )
                    self.current_scope = self.block_scopes.get(label, "global")
                    for instr in instrs:
                        reti_instrs, idx = self._reti_instr(instr, idx, block)
                        instrs_block_free += self._inherit_origin_many(
                            reti_instrs, instr
                        )
                case pn.SingleLineComment():
                    instrs_block_free.append(entry)
                case _:
                    instrs_block_free.append(entry)
        return instrs_block_free

    def _entry_size(self, entry):
        match entry:
            case pn.SingleLineComment():
                return 0
            case _:
                return 1

    def _entries_size(self, entries):
        return sum(self._entry_size(entry) for entry in entries)

    def reti(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), sections):
                ivt_entries = []
                text_entries = []
                data_entries = []
                for section in sections:
                    match section:
                        case pn.Section("interrupt_vector_table", section_entries):
                            ivt_entries.extend(section_entries)
                        case pn.Section("text", section_entries):
                            text_entries.extend(
                                self._flatten_text_blocks(section_entries)
                            )
                        case pn.Section("data", section_entries):
                            data_entries.extend(section_entries)
                        case _:
                            throw_error(section)
                self.reti_sections = {
                    "codesegment_start": self._entries_size(ivt_entries),
                    "datasegment_start": self._entries_size(ivt_entries)
                    + self._entries_size(text_entries),
                }
                output_entries = ivt_entries + text_entries + data_entries
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti"),
                    output_entries,
                )
            case _:
                throw_error(file)
