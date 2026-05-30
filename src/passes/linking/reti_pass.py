from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error


class RetiPass:
    # =========================================================================
    # =                                  RETI                                 =
    # =========================================================================
    # - keine Blöcke mehr, Knoten genauso zusammengefügt, wie sie in entfernten Blöcken angeordnet waren
    # - GoTo(Name(str)) werden duch einen Immediate mit passender Distanz / Adresse oder einen Sprungbefehl mit passender Distanz Jump(Always(), Im(str(distance))) ersetzt.

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

    def _reti_instr(self, instr, idx, current_block):
        match instr:
            case rn.Jump(rn.Always(), rn.Name(val)):
                other_block = self.all_blocks[val]
                distance_idx = idx + 3 if global_vars.args.no_long_jumps else idx
                distance = self._determine_distance(
                    current_block, other_block, distance_idx
                )
                instrs = self._patch_too_large_jumps(rn.Always(), distance, instr)
                return instrs, distance_idx + 1
            case rn.Jump(rn.Eq() as rel, pn.GoTo(pn.Name(val))):
                other_block = self.all_blocks[val]
                distance_idx = idx + 4 if global_vars.args.no_long_jumps else idx
                distance = self._determine_distance(
                    current_block, other_block, distance_idx
                )
                instrs = self._patch_too_large_jumps(rel, distance, instr)
                return instrs, distance_idx + 1
            case rn.Instr((rn.Loadin() | rn.Storein() | rn.Tsl()), [_, _, rn.Name(val)]):
                var_name = val
                symbol, _ = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                match symbol:
                    case {
                        "type_qual": _,
                        "datatype": _,
                        "name": _,
                        "addr": addr,
                        "size": _,
                    }:
                        instr.args[2] = rn.Im(addr)
                        return [instr], idx + 1
            case rn.Instr(
                (rn.Loadin() | rn.Storein() | rn.Tsl()),
                [_, _, rn.BinOp(rn.Name(val), op, num)],
            ):
                var_name = val
                symbol, _ = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                match symbol:
                    case {
                        "type_qual": _,
                        "datatype": _,
                        "name": _,
                        "addr": addr,
                        "size": _,
                    }:
                        match op:
                            case rn.Add():
                                instr.args[2] = rn.Im(addr + num)
                            case rn.Sub():
                                instr.args[2] = rn.Im(addr - num)
                        return [instr], idx + 1
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
            case rn.Instr(rn.Loadi(), [_, rn.Name(val)]):
                if self._is_function_label(val):
                    instr.args[1] = rn.Im(self.all_blocks[val].instrs_before.val)
                    return [instr], idx + 1
                var_name = val
                symbol, _ = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                match symbol:
                    case {
                        "type_qual": _,
                        "datatype": _,
                        "name": _,
                        "addr": addr,
                        "size": _,
                    }:
                        instr.args[1] = rn.Im(addr)
                        return [instr], idx + 1
            case pn.SingleLineComment():
                return [instr], idx
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
