from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error
import copy


class PicocAnfPass:
    def _epilogue_label(self, fun_name):
        return f"{fun_name}_epilogue"

    def _append_epilogue_block(self, blocks_out, fun_name, section):
        epilogue = pn.Block(
            self._epilogue_label(fun_name),
            [
                pn.RestoreStackframe(),
                pn.RestoreReturnAddress(),
            ],
        )
        epilogue.section = section
        self._register_block(epilogue, fun_name)
        blocks_out.append(epilogue)

    # This strips repeated final ".<id>" and "_cont" parts, so the next label
    # becomes if_cont.7, not if.4_cont.6_cont.7 
    def _block_label_base(self, block_name):
        # Both suffixes can appear together, so keep stripping until the base
        # remains: if_cont.6 -> if_cont -> if.
        while True:
            # rsplit(..., 1) returns either [name] or [name, suffix], so
            # len(label_parts) == 2 is needed before reading label_parts[1].
            label_parts = block_name.rsplit(".", 1)
            if len(label_parts) == 2 and label_parts[1].isdigit():
                block_name = label_parts[0]
                continue
            if block_name.endswith("_cont"):
                block_name = block_name.removesuffix("_cont")
                continue
            return block_name

    def _new_call_cont_label(self, block_name):
        label_base = self._block_label_base(block_name)
        base = f"{label_base}_cont"
        while True:
            label = f"{base}.{self.block_idx}"
            if label not in self.all_blocks:
                return label
            self.block_idx += 1

    def _set_save_return_address_label(self, stmts, call_idx, label):
        save_return_address_offset = getattr(
            stmts[call_idx], "save_return_address_offset", None
        )
        if save_return_address_offset is None:
            throw_error("Function call GoTo has no SaveReturnAddress offset")

        save_return_address_idx = call_idx - save_return_address_offset
        match stmts[save_return_address_idx]:
            case pn.SaveReturnAddress(pn.Empty()) as save_return_address:
                save_return_address.label = pn.Name(label)
                return
        throw_error("Function call continuation has no SaveReturnAddress")

    def _register_block(self, block, scope):
        match block:
            case pn.Block(block_name, _):
                block.block_idx = self.block_idx
                self.block_idx += 1
                self.all_blocks[block_name] = block
                self.block_scopes[block_name] = scope
            case _:
                throw_error(block)

    def _argument_word_size(self, exp):
        match self._exp_result_datatype(exp):
            case pn.ArrayDecl():
                return 1
            case pn.VoidType():
                return 0
            case None:
                return 1
            case datatype:
                return self._datatype_size(datatype)

    def _call_argument_word_size(self, exps):
        return sum(self._argument_word_size(exp) for exp in exps)

    def _split_call_continuations(self, block, blocks_out):
        match block:
            case pn.Block(block_name, stmts):
                for idx, stmt in enumerate(stmts):
                    match stmt:
                        case pn.Exp(pn.GoTo(pn.Stack(pn.Num("1")))):
                            # Only function-call jumps need continuation splitting.
                            if getattr(stmt, "save_return_address_offset", None) is None:
                                continue

                            cont_stmts = stmts[idx + 1 :]
                            if not cont_stmts:
                                # Only possible if the implicit void return was removed;
                                # otherwise calls continue at return/return-expr nodes.
                                throw_error(
                                    f"Function call in block '{block_name}' has no continuation"
                                )

                            cont_label = self._new_call_cont_label(block_name)
                            self._set_save_return_address_label(
                                stmts, idx, cont_label
                            )
                            block.stmts_instrs = stmts[: idx + 1]
                            # Append before recursively splitting the continuation, so
                            # each *_cont.N block stays next to the part it came from.
                            blocks_out.append(block)

                            cont_block = pn.Block(cont_label, cont_stmts)
                            cont_block.section = getattr(block, "section", None)
                            self._register_block(
                                cont_block,
                                self.block_scopes.get(block_name, "global"),
                            )
                            self._split_call_continuations(cont_block, blocks_out)
                            return
                # No function-call jump was found, so the block stays unchanged.
                blocks_out.append(block)
            case _:
                throw_error(block)

    def _picoc_anf_exp(self, exp, addr_calc=False):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case (pn.Global() | pn.StackframeLocalVar() | pn.StackframeParam()) as loc:
                datatype = loc.datatype
                if addr_calc:
                    match datatype:
                        case (
                            pn.StructSpec()
                            | pn.ArrayDecl()
                            | pn.PntrDecl()
                            | pn.FunPtrDecl()
                            | pn.IntType()
                            | pn.CharType()
                        ):
                            return [pn.Ref(loc)]
                        case _:
                            throw_error(datatype)
                else:
                    match datatype:
                        case pn.StructSpec():
                            if self.argmode_on:
                                # struct gets passed by value
                                size_val = self._datatype_size(datatype)
                                return [pn.Assign(pn.Stack(pn.Num(str(size_val))), loc)]
                            return [pn.Exp(loc)]
                        case pn.ArrayDecl():
                            return [pn.Ref(loc)]
                        case (
                            pn.PntrDecl()
                            | pn.FunPtrDecl()
                            | pn.IntType()
                            | pn.CharType()
                        ):
                            return [pn.Exp(loc)]
                        case _:
                            throw_error(datatype)
            case pn.Num() | pn.Char():
                return [pn.Exp(exp)]
            case pn.FunRef():
                return [pn.Exp(exp)]
            case pn.Call(pn.Name("print") as name, [exp]):
                exp_anf = self._picoc_anf_exp(exp)
                return exp_anf + [pn.Exp(pn.Call(name, [pn.Stack(pn.Num("1"))]))]
            case pn.Call(pn.Name("input"), []):
                return [pn.Exp(exp)]
            case pn.Asm():
                return [pn.Exp(exp)]
            case pn.SizeOf(exp_datatype):
                size = 1
                if isinstance(
                    exp_datatype,
                    (
                        pn.IntType,
                        pn.CharType,
                        pn.VoidType,
                        pn.StructSpec,
                        pn.ArrayDecl,
                        pn.PntrDecl,
                        pn.FunPtrDecl,
                    ),
                ):
                    size = self._datatype_size(exp_datatype)
                else:
                    match exp_datatype:
                        case pn.Name(val):
                            symbol, _ = self.symbol_table.resolve(
                                val, scope=self.current_scope
                            )
                            size = self._datatype_size(symbol["datatype"])
                        case pn.Cast(datatype, _):
                            size = self._datatype_size(datatype)
                        case (
                            pn.BinOp()
                            | pn.Subscr()
                            | pn.Deref()
                            | pn.Attr()
                            | pn.Num()
                            | pn.Char()
                            | pn.UnOp()
                            | pn.Ref()
                        ):
                            pass
                        case _:
                            size = self._datatype_size(exp_datatype)
                return [pn.Exp(pn.SizeOf(size))]
            case pn.Exit(pn.Num(val)):
                return [exp_datatype]
            # ----------------------- L_Arith + L_Logic -----------------------
            case pn.BinOp(left_exp, bin_op, right_exp) as binop_exp:
                def _skip_deref_after(exp):
                    return isinstance(exp, (pn.Call, pn.BinOp, pn.Ref)) or (
                        isinstance(exp, pn.Cast)
                        and isinstance(exp.exp, (pn.Call, pn.BinOp, pn.Ref))
                    )
                left_dt = self._exp_result_datatype(left_exp)
                right_dt = self._exp_result_datatype(right_exp)
                result_dt = self._exp_result_datatype(binop_exp)
                left_addr_calc = isinstance(
                    left_dt, (pn.PntrDecl, pn.ArrayDecl, pn.StructSpec)
                )
                right_addr_calc = isinstance(
                    right_dt, (pn.PntrDecl, pn.ArrayDecl, pn.StructSpec)
                )
                match left_exp:
                    case pn.Num("0"):
                        left_is_zero = True
                    case _:
                        left_is_zero = False
                match right_exp:
                    case pn.Num("0"):
                        right_is_zero = True
                    case _:
                        right_is_zero = False
                if isinstance(bin_op, (pn.Add, pn.Sub)) and left_is_zero:
                    exps1_anf = []
                else:
                    exps1_anf = self._picoc_anf_exp(left_exp, left_addr_calc)
                match left_dt:
                    case pn.PntrDecl():
                        exps1_anf += (
                            []
                            if _skip_deref_after(left_exp)
                            else [pn.Exp(pn.Deref(pn.Stack(pn.Num("1"), left_dt)))]
                        )
                if isinstance(bin_op, (pn.Add, pn.Sub)) and right_is_zero:
                    exps2_anf = []
                else:
                    exps2_anf = self._picoc_anf_exp(right_exp, right_addr_calc)
                match right_dt:
                    case pn.PntrDecl():
                        exps2_anf += (
                            []
                            if _skip_deref_after(right_exp)
                            else [pn.Exp(pn.Deref(pn.Stack(pn.Num("1"), right_dt)))]
                        )
                if isinstance(bin_op, (pn.Add, pn.Sub)) and (left_is_zero or right_is_zero):
                    return exps1_anf + exps2_anf
                binop = pn.BinOp(
                    pn.Stack(pn.Num("2"), left_dt),
                    bin_op,
                    pn.Stack(pn.Num("1"), right_dt),
                    result_dt,
                )
                return exps1_anf + exps2_anf + [pn.Exp(binop)]
            case pn.UnOp(un_op, exp):
                exps_anf = self._picoc_anf_exp(exp)
                match exp:
                    case pn.Num(val):
                        if val == "2147483648":
                            return [pn.Exp(pn.Num("-2147483648"))]
                return exps_anf + [pn.Exp(pn.UnOp(un_op, pn.Stack(pn.Num("1"))))]
            case pn.PostInc(inner_exp):
                exp_anf = self._picoc_anf_exp(copy.deepcopy(inner_exp))
                assign_anf = self._picoc_anf_stmt(
                    pn.Assign(
                        copy.deepcopy(inner_exp),
                        pn.BinOp(copy.deepcopy(inner_exp), pn.Add(), pn.Num("1")),
                    )
                )
                return exp_anf + assign_anf
            case pn.PostDec(inner_exp):
                exp_anf = self._picoc_anf_exp(copy.deepcopy(inner_exp))
                assign_anf = self._picoc_anf_stmt(
                    pn.Assign(
                        copy.deepcopy(inner_exp),
                        pn.BinOp(copy.deepcopy(inner_exp), pn.Sub(), pn.Num("1")),
                    )
                )
                return exp_anf + assign_anf
            case pn.Cast(datatype, inner_exp):
                inner_dt = self._exp_result_datatype(inner_exp)
                exps_anf = self._picoc_anf_exp(inner_exp, addr_calc=addr_calc)
                return exps_anf + [
                    pn.Exp(pn.Cast(copy.deepcopy(datatype), pn.Stack(pn.Num("1"), inner_dt)))
                ]
            # ---------------------------- L_Logic ----------------------------
            case pn.Atom(left_exp, rel, right_exp):
                exps1_anf = self._picoc_anf_exp(left_exp)
                exps2_anf = self._picoc_anf_exp(right_exp)
                return (
                    exps1_anf
                    + exps2_anf
                    + [
                        pn.Exp(
                            pn.Atom(
                                pn.Stack(pn.Num("2")),
                                rel,
                                pn.Stack(pn.Num("1")),
                            )
                        )
                    ]
                )
            case pn.ToBool(exp):
                exps_anf = self._picoc_anf_exp(exp)
                return exps_anf + [pn.Exp(pn.ToBool(pn.Stack(pn.Num("1"))))]
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Alloc():
                return []
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Deref(inner_exp, datatype):
                exp_anf = self._picoc_anf_exp(inner_exp, addr_calc=True)
                return exp_anf + ([] if addr_calc else [pn.Exp(pn.Deref(pn.Stack(pn.Num("1"), self._deref_result_datatype(datatype))))])
            case pn.Attr(inner_exp, pn.Name(attr_name), datatype):
                offset = self._struct_attr_offset(datatype, attr_name)
                binop = pn.BinOp(inner_exp, pn.Add(), pn.Num(str(offset)), datatype)
                exp_anf = self._picoc_anf_exp(binop, addr_calc=True)
                return exp_anf + ([] if addr_calc else [pn.Exp(pn.Deref(pn.Stack(pn.Num("1"), self._attr_result_datatype(datatype, attr_name))))])
            # ----------------------------- L_Pntr ----------------------------
            case pn.Ref(ref):
                return self._picoc_anf_exp(ref, addr_calc=True)
            # ---------------------------- L_Array ----------------------------
            case pn.Array(exps):
                exps_anf = []
                for exp in exps:
                    exps_anf += self._picoc_anf_exp(exp)
                return exps_anf
            # ---------------------------- L_Struct ---------------------------
            case pn.Struct(init_pairs):
                exps_anf = []
                for init_pair in init_pairs:
                    match init_pair:
                        case pn.InitPair(_, exp):
                            exps_anf += self._picoc_anf_exp(exp)
                        case _:
                            throw_error(init_pair)
                return exps_anf
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(fun_exp, exps, datatype):
                exps_anf = []
                self.argmode_on = True
                for exp2 in reversed(exps):
                    exps_anf += self._picoc_anf_exp(exp2)
                self.argmode_on = False

                return_type = datatype
                match fun_exp:
                    case pn.Name():
                        callee_anf = [pn.Exp(pn.FunRef(copy.deepcopy(fun_exp)))]
                    case _:
                        callee_anf = self._picoc_anf_exp(fun_exp)

                call_goto = pn.Exp(pn.GoTo(pn.Stack(pn.Num("1"))))
                call_goto.save_return_address_offset = len(callee_anf) + 1
                remove_arguments = pn.RemoveArguments(
                    pn.Num(str(self._call_argument_word_size(exps)))
                )

                return (
                    self._single_line_comment(exp, "//")
                    + exps_anf
                    + [pn.SaveReturnAddress()]
                    + callee_anf
                    + [
                        call_goto,
                        remove_arguments,
                    ]
                    + (
                        [pn.Exp(rn.Reg(rn.In2()))]
                        if not isinstance(return_type, pn.VoidType)
                        else []
                    )
                )
            # ---------------------------- L_Misc -----------------------------
            case pn.Debug():
                return [pn.Exp(exp)]
            case _:
                throw_error(exp)

    def _picoc_anf_stmt(self, stmt):
        match stmt:
            # --------------------------- L_Comment ---------------------------
            case pn.SingleLineComment():
                return [stmt]
            # ----------------------- L_Array + L_Struct ----------------------
            case pn.Assign(
                pn.Alloc(_, datatype, name) as alloc,
                (pn.Array(_) | pn.Struct(_)) as array_struct,
            ):
                # this has to be in this order because the datatype declarator
                # has to be reversed in the _picoc_mon_exp call
                # TODO: ugly solution and add it again
                #  array_struct.datatype = alloc.datatype
                #  array_struct.visible += (
                #      [array_struct.datatype] if global_vars.args.double_verbose else []
                #  )
                stmt_anf = self._picoc_anf_stmt(
                    pn.Assign(self._picoc_rewrite_exp(name), array_struct)
                )
                return self._single_line_comment(stmt, "//") + self._inherit_origin_many(stmt_anf, stmt)
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(pn.Global(pn.Name(var_name)) as lhs, exp):
                exps_anf = self._picoc_anf_exp(exp)
                symbol, _ = self.symbol_table.resolve(
                    var_name, scope="global"
                )
                match symbol:
                    case {
                        "type_qual": pn.Writeable(),
                        "datatype": _,
                        "name": _,
                        "addr": _,
                        "size": size,
                    }:
                        num_size = pn.Num(size)
                        return (
                            self._single_line_comment(stmt, "//")
                            + exps_anf
                            + [
                                pn.Assign(
                                    lhs,
                                    pn.Stack(num_size),
                                )
                            ]
                        )
                    case _:
                        throw_error(symbol)
            case pn.Assign((pn.StackframeLocalVar() | pn.StackframeParam()) as lhs, exp):
                exps_anf = self._picoc_anf_exp(exp)
                var_name = lhs.symbol_name
                symbol, _ = (
                    self.symbol_table.resolve(var_name, scope=self.current_scope)
                    if var_name
                    else (None, None)
                )
                match symbol:
                    case {
                        "type_qual": pn.Writeable(),
                        "datatype": _,
                        "name": _,
                        "addr": addr,
                        "size": size,
                    }:
                        num_size = pn.Num(size)
                        target = copy.deepcopy(lhs)
                        target.num = pn.Num(addr)
                        setattr(
                            target, "symbol_name", getattr(lhs, "symbol_name", None)
                        )
                        setattr(target, "datatype", getattr(lhs, "datatype", None))
                        return (
                            self._single_line_comment(stmt, "//")
                            + exps_anf
                            + [
                                pn.Assign(
                                    target,
                                    pn.Stack(num_size),
                                )
                            ]
                        )
                    case _:
                        throw_error(symbol)
            case pn.Assign(ref, exp):
                # Deref, Subscript, Attribute
                exps_anf = self._picoc_anf_exp(exp)
                refs_anf = self._picoc_anf_exp(ref, addr_calc=True)
                return (
                    self._single_line_comment(stmt, "//")
                    + exps_anf
                    + refs_anf
                    + [
                        pn.Assign(
                            pn.Stack(pn.Num("1")),
                            pn.Stack(pn.Num("2")),
                        )
                    ]
                )
            # --------------------- L_Assign_Alloc + L_Fun --------------------
            case pn.Exp(alloc_call):
                exps_anf = self._picoc_anf_exp(alloc_call)
                return self._single_line_comment(stmt, "//") + exps_anf
            # ----------------------- L_If_Else + L_Loop ----------------------
            case pn.IfElse(exp, goto1_list, goto2_list):
                exps_anf = self._picoc_anf_exp(exp)
                return (
                    self._single_line_comment(stmt, "//")
                    + exps_anf
                    + [pn.IfElse(pn.Stack(pn.Num("1")), goto1_list, goto2_list)]
                )
            # ----------------------------- L_Fun -----------------------------
            case pn.NewStackframe():
                stmt.call_target_function = self.current_scope
                stmt.indirect_call = False
                return [stmt]
            case pn.Return(pn.Empty()):
                return [
                    pn.Exp(pn.GoTo(pn.Name(self._epilogue_label(self.current_scope))))
                ]
            case pn.Return(exp):
                exps_anf = self._picoc_anf_exp(exp)
                return exps_anf + [
                    pn.Assign(rn.Reg(rn.In2()), pn.Stack(pn.Num("1"))),
                    pn.Exp(pn.GoTo(pn.Name(self._epilogue_label(self.current_scope)))),
                ]
            # ---------------------------- L_Block ----------------------------
            case pn.GoTo(pn.Name(val)):
                return [pn.Exp(stmt)]
            # ---------------------------- L_Misc -----------------------------
            case pn.Debug():
                return [pn.Exp(stmt)]
            case _:
                throw_error(stmt)

    def picoc_anf(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), blocks):
                blocks_anf = []
                current_function = None
                current_function_section = None
                for block in blocks:
                    label = block.name
                    block_scope = self.block_scopes.get(label, "global")
                    if current_function is not None and block_scope != current_function:
                        self._append_epilogue_block(
                            blocks_anf,
                            current_function,
                            current_function_section,
                        )
                        current_function = None
                        current_function_section = None

                    self.current_scope = block_scope
                    self.next_local_addr = self.fun_local_sizes.get(self.current_scope, 0)
                    match block:
                        case pn.Block(_, stmts):
                            if block_scope != "global":
                                current_function = block_scope
                                current_function_section = getattr(block, "section", None)
                            stmts_anf = []
                            for stmt in stmts:
                                stmts_anf += self._inherit_origin_many(
                                    self._picoc_anf_stmt(stmt), stmt
                                )
                            block.stmts_instrs[:] = stmts_anf
                            self._split_call_continuations(block, blocks_anf)
                        case _:
                            throw_error(block)
                if current_function is not None:
                    self._append_epilogue_block(
                        blocks_anf,
                        current_function,
                        current_function_section,
                    )
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_anf"),
                    blocks_anf,
                )
            case _:
                throw_error(file)
