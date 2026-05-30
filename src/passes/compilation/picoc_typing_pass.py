from src import global_vars
from src import picoc_nodes as pn
from src.utils.util_funs_dependent import throw_error
import copy


class PicocTypingPass:
    def _deref_result_datatype(self, pointer_dt):
        match pointer_dt:
            case pn.PntrDecl(inner_dt):
                return copy.deepcopy(inner_dt)
            case pn.ArrayDecl(_, inner_dt):
                return copy.deepcopy(inner_dt)
            case _:
                throw_error(pointer_dt)

    def _ref_result_datatype(self, inner_dt):
        return pn.PntrDecl(copy.deepcopy(inner_dt))

    def _call_return_datatype(self, fun_dt):
        match fun_dt:
            case pn.FunDecl(_, ret_dt, _, _):
                return copy.deepcopy(ret_dt)
            case pn.PntrDecl(pn.FunPtrDecl(ret_dt, _)):
                return copy.deepcopy(ret_dt)
            case pn.FunPtrDecl(ret_dt, _):
                return copy.deepcopy(ret_dt)
            case _:
                throw_error(fun_dt)

    def _attr_result_datatype(self, struct_dt, attr_name: str):
        match struct_dt:
            case pn.StructSpec(pn.Name(struct_name)):
                symbol, _ = self.symbol_table.resolve(attr_name, scope=struct_name)
                if symbol is None:
                    struct_symbol, _ = self.symbol_table.resolve(
                        struct_name, scope=self.current_scope
                    )
                    if struct_symbol is not None and not struct_symbol.get(
                        "complete", True
                    ):
                        throw_error(
                            f"Invalid member access on incomplete struct type '{struct_name}'; "
                            f"the full struct declaration is required"
                        )
                    throw_error(
                        f"Struct '{struct_name}' has no member named '{attr_name}'"
                    )
                return copy.deepcopy(symbol["datatype"])
            case _:
                throw_error(struct_dt)

    def _exp_result_datatype(self, exp):
        match exp:
            case pn.Deref(_, datatype):
                return self._deref_result_datatype(datatype)
            case pn.Attr(_, pn.Name(attr_name), datatype):
                return self._attr_result_datatype(datatype, attr_name)
            case pn.Ref(inner_exp):
                inner_dt = self._exp_result_datatype(inner_exp) # TODO: warum ist Datatype hicht schon in Ref?
                return self._ref_result_datatype(inner_dt)
            case pn.Cast(datatype, _):
                return copy.deepcopy(datatype)
        datatype = getattr(exp, "datatype", None)
        if datatype is not None:
            return copy.deepcopy(datatype)
        match exp:
            case pn.Num():
                return pn.IntType()
            case pn.Char():
                return pn.CharType()
            case _:
                return None

    def _struct_attr_offset(self, struct_dt, attr_name: str) -> int:
        match struct_dt:
            case pn.StructSpec(pn.Name(struct_name)):
                struct_sym, _ = self.symbol_table.resolve(
                    struct_name, scope=self.current_scope
                )
                if struct_sym is None:
                    throw_error(
                        f"Invalid member access on undefined struct type '{struct_name}'"
                    )
                if not struct_sym.get("complete", True):
                    throw_error(
                        f"Invalid member access on incomplete struct type '{struct_name}'; "
                        f"the full struct declaration is required"
                    )
                attr_ids = struct_sym["attrs"]
                rel_pos_in_struct = 0
                for attr_id in attr_ids:
                    if attr_id.val == attr_name:
                        return int(rel_pos_in_struct)
                    attr_sym, _ = self.symbol_table.resolve(
                        attr_id.val, scope=struct_name
                    )
                    rel_pos_in_struct += int(attr_sym["size"])

                throw_error((struct_name, attr_name))
            case _:
                throw_error(struct_dt)

    def _picoc_type_exp(self, exp):
        match exp:
            # ----------------------------- L_Arith ------------------------------
            case pn.Num():
                exp.datatype = pn.IntType()
                return pn.IntType()
            case pn.Char():
                exp.datatype = pn.IntType()
                return pn.CharType()
            case pn.Global(pn.Name(val)):
                symbol, _ = self.symbol_table.resolve(val, scope="global")
                dt = copy.deepcopy(symbol["datatype"])
                exp.datatype = copy.deepcopy(dt)
                return dt
            case pn.FunRef(_, datatype):
                dt = copy.deepcopy(datatype)
                return dt
            case pn.Stackframe():
                symbol_name = exp.symbol_name
                symbol, _ = self.symbol_table.resolve(symbol_name, scope=self.current_scope)
                dt = copy.deepcopy(symbol["datatype"])
                exp.datatype = copy.deepcopy(dt)
                return dt
            # TODO: can probably be removed
            # case pn.Name(val):
            #     symbol, _ = self.symbol_table.resolve(val, scope=self.current_scope)
            #     dt = copy.deepcopy(symbol["datatype"]) if symbol else None
            #     exp.datatype = copy.deepcopy(dt)
            #     return dt
            case pn.BinOp(left_exp, bin_op, right_exp):
                l_dt = self._picoc_type_exp(left_exp)
                r_dt = self._picoc_type_exp(right_exp)
                if isinstance(bin_op, (pn.Add, pn.Sub)):
                    if isinstance(l_dt, (pn.PntrDecl, pn.ArrayDecl)):
                        exp.datatype = copy.deepcopy(l_dt)
                        return copy.deepcopy(l_dt)
                    if isinstance(r_dt, (pn.PntrDecl, pn.ArrayDecl)):
                        exp.datatype = copy.deepcopy(r_dt)
                        return copy.deepcopy(r_dt)
                exp.datatype = pn.IntType()
                return pn.IntType()
            case pn.Cast(datatype, inner_exp):
                _ = self._picoc_type_exp(inner_exp)
                return copy.deepcopy(datatype)
            case pn.UnOp(un_op, inner_exp):
                _ = self._picoc_type_exp(inner_exp)
                exp.datatype = pn.IntType()
                return pn.IntType()
            case pn.PostInc(inner_exp) | pn.PostDec(inner_exp):
                inner_dt = self._picoc_type_exp(inner_exp)
                exp.datatype = copy.deepcopy(inner_dt)
                return copy.deepcopy(inner_dt)
            case pn.SizeOf(exp_datatype):
                # _ = self._picoc_type_exp(exp_datatype)
                exp.datatype = pn.IntType()
                return pn.IntType()
            # ----------------------------- L_Logic ------------------------------
            case pn.Atom(left_exp, _, right_exp):
                self._picoc_type_exp(left_exp)
                self._picoc_type_exp(right_exp)
                exp.datatype = pn.IntType()
                return pn.IntType()
            case pn.ToBool(inner_exp): # TODO: What is with pointer?
                self._picoc_type_exp(inner_exp)
                return pn.IntType()
            # ------------------------ L_Pntr + L_Array -------------------------
            case pn.Ref(inner_exp):
                inner_dt = self._picoc_type_exp(inner_exp)
                ref_dt = self._ref_result_datatype(inner_dt)
                exp.datatype = copy.deepcopy(ref_dt)
                return ref_dt
            case pn.Deref(addr_exp):
                base_dt = self._picoc_type_exp(addr_exp)
                exp.datatype = copy.deepcopy(base_dt)
                return self._deref_result_datatype(base_dt) if base_dt else None
            case pn.Array(exps):
                for i, exp in enumerate(exps):
                    if i == 0:
                        elem_dt = self._picoc_type_exp(exp)
                    else:
                        self._picoc_type_exp(exp)
                return pn.ArrayDecl(pn.Num(str(len(exps))), elem_dt)
            # ----------------------------- L_Struct ----------------------------
            case pn.Struct(init_pairs):
                for init_pair in init_pairs:
                    match init_pair:
                        case pn.InitPair(_, inner_exp):
                            self._picoc_type_exp(inner_exp)
                        case _:
                            throw_error(init_pair)
                return None
            case pn.Attr(inner_exp, pn.Name(attr_name)):
                base_dt = self._picoc_type_exp(inner_exp)
                exp.datatype = copy.deepcopy(base_dt)
                return self._attr_result_datatype(base_dt, attr_name)
            case pn.Exit():
                return None
            case pn.Asm():
                return None
            # ------------------------------ L_Fun ------------------------------
            # TODO: Problem with linking, if function defined in other file
            case pn.Call(pn.Name(fun_name), exps):
                for inner_exp in exps:
                    self._picoc_type_exp(inner_exp)
                symbol, _ = self.symbol_table.resolve(fun_name, scope="global")
                match symbol:
                    case {"datatype": pn.FunDecl(_, ret_dt, _, _)}:
                        exp.datatype = copy.deepcopy(ret_dt)
                        return copy.deepcopy(ret_dt)
                    case _:
                        throw_error(symbol)
            case pn.Call(fun_exp, exps):
                fun_dt = self._picoc_type_exp(fun_exp)
                for inner_exp in exps:
                    self._picoc_type_exp(inner_exp)
                ret_dt = self._call_return_datatype(fun_dt)
                exp.datatype = copy.deepcopy(ret_dt)
                return ret_dt
            case pn.Empty():
                return None
            case _:
                throw_error(exp)

    def _picoc_type_stmt(self, stmt):
        match stmt:
            case pn.Assign(pn.Alloc(), exp):
                self._picoc_type_exp(exp)
                return [stmt]
            case pn.Assign(lhs, exp):
                self._picoc_type_exp(lhs)
                self._picoc_type_exp(exp)
                return [stmt]
            case pn.Exp(exp):
                self._picoc_type_exp(exp)
                return [stmt]
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                self._picoc_type_exp(exp)
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_type_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            case pn.IfElse(exp, stmts1, stmts2):
                self._picoc_type_exp(exp)
                new_stmts1 = []
                for inner_stmt in stmts1:
                    new_stmts1 += self._picoc_type_stmt(inner_stmt)
                new_stmts2 = []
                for inner_stmt in stmts2:
                    new_stmts2 += self._picoc_type_stmt(inner_stmt)
                stmt.stmts1 = new_stmts1
                stmt.stmts2 = new_stmts2
                return [stmt]
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                self._picoc_type_exp(exp)
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_type_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            case pn.DoWhile(exp, stmts):
                self._picoc_type_exp(exp)
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_type_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            # ----------------------------- L_Fun -----------------------------
            case pn.Return(pn.Empty()):
                return [stmt]
            case pn.Return(exp):
                self._picoc_type_exp(exp)
                return [stmt]
            case pn.StackMalloc():
                return [stmt]
            case pn.GoTo():
                return [stmt]
            # ---------------------------- L_Misc -----------------------------
            case pn.Debug() | pn.SingleLineComment():
                return [stmt]
            case _:
                throw_error(stmt)

    def picoc_typing(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(_, blocks):
                self.current_scope = "global"
                typed_blocks = []
                for block in blocks:
                    label = getattr(block.name, "val", block.name)
                    self.current_scope = self.block_scopes.get(label, "global")
                    match block:
                        case pn.Block(_, stmts):
                            new_stmts = []
                            for stmt in stmts:
                                new_stmts += self._picoc_type_stmt(stmt)
                            block.stmts_instrs = new_stmts
                            typed_blocks.append(block)
                        case _:
                            throw_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_typing"),
                    typed_blocks,
                )
            case _:
                throw_error(file)
