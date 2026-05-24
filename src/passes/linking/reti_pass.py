from src.passes.dependencies import *


class RetiPass:
    # =========================================================================
    # =                                  RETI                                 =
    # =========================================================================
    # - keine Blöcke mehr, Knoten genauso zusammengefügt, wie sie in entfernten Blöcken angeordnet waren
    # - GoTo(Name(str)) werden duch einen Immediate mit passender Distanz / Adresse oder einen Sprungbefehl mit passender Distanz Jump(Always(), Im(str(distance))) ersetzt.

    # NEG_RELS = {
    #     "": rn.Always(),
    #     "==": rn.Eq(),
    #     "!=": rn.NEq(),
    #     "<": rn.GtE(),
    #     "<=": rn.Gt(),
    #     ">": rn.LtE(),
    #     ">=": rn.Lt(),
    # }
    NEG_RELS = {
        "": rn.Always(),
        "==": rn.NEq(),
        "!=": rn.Eq(),
        "<": rn.GtE(),
        "<=": rn.Gt(),
        ">": rn.LtE(),
        ">=": rn.Lt(),
    }

    def _patch_too_large_jumps(self, rel, distance, instr):
        if global_vars.args.no_long_jumps:
            #  if (
            #  distance < -(2**21) and distance > 2**21 - 1
            #  ) or global_vars.args.no_jump:
            neg_rel = self.NEG_RELS[str(rel)]
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
                distance = self._determine_distance(current_block, other_block, idx)
                return self._patch_too_large_jumps(rn.Always(), distance, instr)
            case rn.Jump(rn.Eq() as rel, pn.GoTo(pn.Name(val))):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return self._patch_too_large_jumps(rel, distance, instr)
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
                        return [instr]
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
                        return [instr]
            case rn.Instr(
                rn.Loadi(),
                [
                    rn.Reg(rn.Acc()) as reg,
                    rn.BinOp(rn.Name("_this_instruction"), rn.Add(), constant),
                ],
            ):
                rel_addr = str(int(current_block.instrs_before.val) + idx + constant)
                return self._single_line_comment(instr, "#") + [
                    rn.Instr(rn.Loadi(), [reg, rn.Im(rel_addr)])
                ]
            case rn.Instr(rn.Loadi(), [_, rn.Name(val)]):
                if self._is_function_label(val):
                    instr.args[1] = rn.Im(self.all_blocks[val].instrs_before.val)
                    return [instr]
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
                        return [instr]
            case _:
                return [instr]

    def reti(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), blocks):
                instrs_block_free = []
                for block in blocks:
                    match block:
                        case pn.Block(name, instrs):
                            idx = 0
                            instrs_block_free += self._single_line_comment(
                                pn.Block(name, []), "# //"
                            )
                            label = block.name
                            self.current_scope = self.block_scopes.get(label, "global")
                            for instr in instrs:
                                match instr:
                                    case rn.Jump(
                                        rn.Always(), rn.Name()
                                    ) if global_vars.args.no_long_jumps:
                                        idx += 3
                                    case rn.Jump(
                                        rn.Eq(), pn.GoTo()
                                    ) if global_vars.args.no_long_jumps:
                                        idx += 4
                                    case _:
                                        pass
                                instrs_block_free += self._inherit_origin_many(
                                    self._reti_instr(instr, idx, block), instr
                                )
                                match instr:
                                    case pn.SingleLineComment():
                                        pass
                                    case _:
                                        idx += 1
                        case _:
                            throw_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti"),
                    instrs_block_free,
                )
            case _:
                throw_error(file)
