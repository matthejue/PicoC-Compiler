from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error


class RetiPass:
    def _negated_rel(self, rel):
        match rel:
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
            case rn.NOp():
                return rn.NOp()
            case _:
                throw_error(rel)

    def _is_function_label(self, name):
        symbol, _ = self.symbol_table.resolve(name, scope="global")
        return isinstance(symbol, dict) and isinstance(symbol.get("datatype"), pn.FunDecl)

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

    def _load_address_operand(self, operand, idx, current_block):
        match operand:
            # Immediate LOADI32 is supported for user-written .reti_blocks only.
            # PicoC-generated code reaches LOADI32 through symbolic addresses.
            case rn.Im(val):
                return int(val)
            case rn.Name(name):
                if self._is_function_label(name):
                    return int(self.all_blocks[name].instrs_before.val)
                return int(self._symbol_addr(name))
            case rn.BinOp(rn.Name("_this_instruction"), rn.Add(), constant):
                return int(current_block.instrs_before.val) + idx + int(constant)
            case _:
                throw_error(f"Unsupported LOADI32 operand: {operand}")

    def _expand_loadi32(self, reg, operand, idx, current_block):
        return self._write_large_immediate_in_register(
            reg, self._load_address_operand(operand, idx, current_block)
        )

    def _jump_target_distance(self, target, idx, current_block):
        match target:
            case rn.Name(target_name):
                target_offset = 0
            case rn.BinOp(rn.Name(target_name), op, num):
                match op:
                    case rn.Add():
                        target_offset = int(num)
                    case rn.Sub():
                        target_offset = -int(num)
                    case _:
                        throw_error(op)
            case _:
                throw_error(f"Unsupported JUMP target: {target}")

        if target_name not in self.all_blocks:
            throw_error(f"JUMP target is not a known block: {target_name}")

        target_block = self.all_blocks[target_name]
        return (
            int(target_block.instrs_before.val)
            + target_offset
            - int(current_block.instrs_before.val)
            - idx
        )

    def _jump32_target_instrs(self, target):
        match target:
            case rn.Name(target_name):
                if target_name not in self.all_blocks:
                    throw_error(f"JUMP32 target is not a known block: {target_name}")

                return (
                    self._write_large_immediate_in_register(
                        rn.Reg(rn.Acc()),
                        int(self.all_blocks[target_name].instrs_before.val),
                    )
                    + [
                        rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                        rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())]),
                    ]
                )
            case rn.BinOp(rn.Name(target_name), op, num):
                if target_name not in self.all_blocks:
                    throw_error(f"JUMP32 target is not a known block: {target_name}")

                addr = int(self.all_blocks[target_name].instrs_before.val)
                match op:
                    case rn.Add():
                        addr += int(num)
                    case rn.Sub():
                        addr -= int(num)
                    case _:
                        throw_error(op)

                return (
                    self._write_large_immediate_in_register(rn.Reg(rn.Acc()), addr)
                    + [
                        rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                        rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())]),
                    ]
                )
            case rn.Im(val):
                # Immediate JUMP32 is supported for user-written .reti_blocks only.
                # PicoC-generated jumps use block labels and add CS after loading.
                return self._write_large_immediate_in_register(
                    rn.Reg(rn.Acc()), int(val)
                ) + [rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())])]
            case _:
                throw_error(f"Unsupported JUMP32 target: {target}")

    def _expand_jump32(self, rel, target):
        target_instrs = self._jump32_target_instrs(target)
        if isinstance(rel, rn.Always):
            return target_instrs

        return [
            rn.Jump(self._negated_rel(rel), rn.Im(str(len(target_instrs) + 1)))
        ] + target_instrs

    def _reti_instr(self, instr, idx, current_block):
        match instr:
            # Resolve the target name to determine the relative jump distance.
            case rn.Jump(rel, rn.Name() | rn.BinOp() as target):
                distance = self._jump_target_distance(target, idx, current_block)
                # The compiler pipeline only emits JUMP32 for symbolic targets.
                # Plain symbolic JUMP can still come from user-written
                # .reti_blocks input, but this short form is not always working:
                # if the resolved relative address needs more than 22 bits, the
                # generated code is intentionally left incorrect instead of
                # being expanded here.
                return [rn.Jump(rel, rn.Im(str(distance)))], idx + 1
            # Expand a symbolic or immediate 32-bit jump into concrete RETI instructions.
            case rn.Jump32(rel, target):
                expanded = self._expand_jump32(rel, target)
                instrs = self._single_line_comment(instr, "#") + expanded
                # JUMP32 expansion length depends on relation and target kind:
                # conditional jumps add a guard, label targets add CS, immediates do not.
                return instrs, idx + len(expanded)
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
            # Expand LOADI32 pseudo instructions into the fixed LOADI/MULTI/ORI sequence.
            case rn.Instr(rn.Loadi32(), [reg, operand]):
                instrs = self._single_line_comment(instr, "#") + self._expand_loadi32(
                    reg, operand, idx, current_block
                )
                # LOADI32 always expands to LOADI/MULTI/ORI, so its size is fixed.
                return instrs, idx + 3
            # Resolve a symbolic LOADI operand to a function, variable, or current-instruction address.
            case rn.Instr(rn.Loadi(), [_, rn.Name() | rn.BinOp() as operand]):
                instr.args[1] = rn.Im(
                    str(self._load_address_operand(operand, idx, current_block))
                )
                # The compiler pipeline only emits LOADI32 for symbolic address
                # loads. Plain symbolic LOADI can still come from user-written
                # .reti_blocks input, but this short form is not always working:
                # if the resolved address needs more than 22 bits, the generated
                # code is intentionally left incorrect instead of being expanded
                # here.
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
