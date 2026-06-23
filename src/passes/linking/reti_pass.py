from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error


class RetiPass:
    IVTE_BASE = 2**31

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

    def _symbolic_operand_value(self, operand, idx, current_block):
        match operand:
            # Immediate values are already concrete.
            case rn.Im(val):
                return int(val)
            case rn.Name(name):
                if name in self.all_blocks:
                    return int(self.all_blocks[name].instrs_before.val)
                return int(self._symbol_addr(name))
            case rn.BinOp(rn.Name(name), op, constant):
                if name in self.all_blocks:
                    value = int(self.all_blocks[name].instrs_before.val)
                else:
                    value = int(self._symbol_addr(name))

                match op:
                    case rn.Add():
                        return value + int(constant)
                    case rn.Sub():
                        return value - int(constant)
                    case _:
                        throw_error(op)
            case _:
                throw_error(f"Unsupported symbolic operand: {operand}")

    def _resolve_symbolic_operand(self, operand, idx, current_block):
        match operand:
            case rn.Name() | rn.BinOp():
                return rn.Im(
                    str(self._symbolic_operand_value(operand, idx, current_block))
                )
            case _:
                return operand

    def _resolve_symbolic_operands(self, operands, idx, current_block):
        return [
            self._resolve_symbolic_operand(operand, idx, current_block)
            for operand in operands
        ]

    def _has_symbolic_operand(self, operands):
        return any(isinstance(operand, (rn.Name, rn.BinOp)) for operand in operands)

    def _ivte_target_address(self, target):
        def block_address(block):
            section_start = getattr(block, "section_start", pn.Num("0"))
            return int(section_start.val) + int(block.instrs_before.val)

        match target:
            case rn.Name(name):
                if name not in self.all_blocks:
                    throw_error(f"Unknown block target for IVTE: {name}")
                return block_address(self.all_blocks[name])
            case rn.BinOp(rn.Name(name), op, constant):
                if name not in self.all_blocks:
                    throw_error(f"Unknown block target for IVTE: {name}")
                address = block_address(self.all_blocks[name])
                match op:
                    case rn.Add():
                        return address + int(constant)
                    case rn.Sub():
                        return address - int(constant)
                    case _:
                        throw_error(op)
            case _:
                throw_error(f"Unsupported IVTE target: {target}")

    def _resolve_ivte(self, entry):
        match entry:
            case rn.Ivte((rn.Name() | rn.BinOp()) as target):
                return rn.Im(str(self.IVTE_BASE + self._ivte_target_address(target)))
            case _:
                return entry

    def _expand_loadi32(self, reg, operand, idx, current_block):
        return self._write_large_immediate_in_register(
            reg, self._symbolic_operand_value(operand, idx, current_block)
        )

    def _jump_target_distance(self, target, idx, current_block):
        return (
            self._symbolic_operand_value(target, idx, current_block)
            - int(current_block.instrs_before.val)
            - idx
        )

    def _jump32_target_instrs(self, target, idx, current_block):
        match target:
            case rn.Name() | rn.BinOp():
                return (
                    self._write_large_immediate_in_register(
                        rn.Reg(rn.Acc()),
                        self._symbolic_operand_value(target, idx, current_block),
                    )
                    + [
                        rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                        rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())]),
                    ]
                )
            case rn.Im(val):
                # Immediate JUMP32 is for e.g. user-written .reti_blocks.
                # PicoC-generated jumps use block labels and add CS after loading.
                return self._write_large_immediate_in_register(
                    rn.Reg(rn.Acc()), int(val)
                ) + [rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())])]
            case _:
                throw_error(f"Unsupported JUMP32 target: {target}")

    def _expand_jump32(self, rel, target, idx, current_block):
        target_instrs = self._jump32_target_instrs(target, idx, current_block)
        if isinstance(rel, rn.Always):
            return target_instrs

        skip_distance = self.count_instrs(target_instrs) + 1
        return [
            rn.Jump(self._negated_rel(rel), rn.Im(str(skip_distance)))
        ] + target_instrs

    def _reti_instr(self, instr, idx, current_block):
        match instr:
            # Expand LOADI32 pseudo instructions into the fixed LOADI/MULTI/ORI sequence.
            case rn.Instr(rn.Loadi32(), [reg, operand]):
                instrs = self._single_line_comment(instr, "#") + self._expand_loadi32(
                    reg, operand, idx, current_block
                )
                # LOADI32 always expands to LOADI/MULTI/ORI, so its size is fixed.
                return instrs, idx + self.count_instrs(instrs)
            # Expand a symbolic or immediate 32-bit jump into concrete RETI instructions.
            case rn.Jump32(rel, target):
                expanded = self._expand_jump32(rel, target, idx, current_block)
                instrs = self._single_line_comment(instr, "#") + expanded
                # JUMP32 expansion length depends on relation and target kind:
                # conditional jumps add a guard, label targets add CS, immediates do not.
                return instrs, idx + self.count_instrs(instrs)
            # Example: IVTE handler writes the SRAM address 2^31 + handler.
            case rn.Ivte(rn.Name() | rn.BinOp()):
                return [self._resolve_ivte(instr)], idx + 1
            # Resolve symbolic interrupt values, e.g. INT syscall_name.
            case rn.Int(rn.Name() | rn.BinOp() as num):
                instr.num = self._resolve_symbolic_operand(num, idx, current_block)
                return [instr], idx + 1
            # Resolve symbolic instruction operands in any parsed operand position.
            case rn.Instr(_, args) if self._has_symbolic_operand(args):
                instr.args[:] = self._resolve_symbolic_operands(
                    args, idx, current_block
                )
                # The compiler pipeline only emits LOADI32 for symbolic address
                # loads. Plain symbolic operands can still come from
                # user-written .reti_blocks input, but short immediate fields
                # are not always working: if the resolved address needs more
                # than 22 bits, the generated code is intentionally left
                # incorrect instead of being expanded here.
                return [instr], idx + 1
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
            # Keep comments in output without increasing the instruction index.
            case pn.SingleLineComment():
                return [instr], idx
            # Already concrete RETI instructions pass through unchanged.
            case _:
                return [instr], idx + 1

    def _flatten_section_blocks(self, entries):
        instrs_block_free = []
        for entry in entries:
            match entry:
                case pn.Block(label, instrs) as block:
                    idx = 0
                    id_comment = pn.block_id_comment(block)
                    if id_comment is not None:
                        instrs_block_free.append(id_comment)
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
                        case pn.Section("ivt", section_entries):
                            ivt_entries.extend(
                                self._flatten_section_blocks(section_entries)
                            )
                        case pn.Section("text", section_entries):
                            text_entries.extend(
                                self._flatten_section_blocks(section_entries)
                            )
                        case pn.Section("data", section_entries):
                            data_entries.extend(
                                self._flatten_section_blocks(section_entries)
                            )
                        case _:
                            throw_error(section)
                self.reti_sections = {
                    "codesegment_start": self._entries_size(ivt_entries),
                    "datasegment_start": self._entries_size(ivt_entries)
                    + self._entries_size(text_entries),
                    "stack_start": -1,
                }
                output_entries = [
                    self._resolve_ivte(entry)
                    for entry in ivt_entries + text_entries + data_entries
                ]
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti"),
                    output_entries,
                )
            case _:
                throw_error(file)
