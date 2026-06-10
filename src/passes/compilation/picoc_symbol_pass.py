from src import global_vars
from src import picoc_nodes as pn
from src.utils.util_funs_dependent import throw_error
import copy


class PicocSymbolPass:
    def _is_variadic_params(self, allocs) -> bool:
        return bool(allocs) and isinstance(allocs[-1], pn.VariadicParam)

    def _fixed_params(self, allocs):
        return [alloc for alloc in allocs if not isinstance(alloc, pn.VariadicParam)]

    def _param_size(self, allocs) -> int:
        size = 0
        for alloc in allocs:
            match alloc:
                case pn.VoidType():
                    continue
                case pn.VariadicParam():
                    continue
                case pn.Alloc(_, pn.ArrayDecl()):
                    size += 1
                case pn.Alloc(_, datatype):
                    size += self._datatype_size(datatype)
                case _:
                    throw_error(alloc)
        return size

    def _datatype_size(self, datatype) -> int:
        match datatype:
            # ------------------------ L_Arith + L_Pntr -----------------------
            case pn.IntType() | pn.CharType() | pn.PntrDecl() | pn.FunPtrDecl():
                return 1
            # ---------------------------- L_Struct ---------------------------
            case pn.StructSpec(pn.Name(val)):
                struct_type_name = val
                symbol, _ = self.symbol_table.resolve(
                    struct_type_name, scope=self.current_scope
                )
                if symbol is None:
                    throw_error(
                        f"Invalid use of undefined struct type '{struct_type_name}'"
                    )
                if not symbol.get("complete", True):
                    throw_error(
                        f"Invalid use of incomplete struct type '{struct_type_name}'; "
                        f"forward-declared structs may only be used through pointers"
                    )
                return int(symbol["size"])
            # ---------------------------- L_Array ----------------------------
            case pn.ArrayDecl(pn.Num(val), datatype2):
                elem_size = self._datatype_size(datatype2)
                return elem_size * int(val)
            case _:
                throw_error(datatype)

    def _declare_alloc(self, alloc, *, initial_val=None, is_param=False):
        match alloc:
            case pn.VoidType():
                return
            case pn.Alloc(type_qual, datatype, pn.Name(val1), _):
                var_name = val1
                datatype_copy = copy.deepcopy(datatype)
                # Parameters of array type decay to pointers to their first element type.
                if is_param and isinstance(
                    datatype_copy, pn.ArrayDecl
                ):
                    datatype_copy = self._ref_result_datatype(datatype_copy.datatype)

                size = self._datatype_size(datatype_copy)
                match self.current_scope:
                    case "global":
                        addr = pn.Empty()
                        frame_kind = "global"
                    case _:
                        if is_param:
                            # Parameter symbols keep a non-negative logical slot
                            # index starting at 0; RetiBlocksPass applies the
                            # concrete ReTI stack offsets when emitting instructions.
                            addr = self.next_param_addr
                            self.next_param_addr += size
                            frame_kind = "param"
                        else:
                            addr = self.next_local_addr + size - 1
                            self.next_local_addr += size
                            frame_kind = "local_var"

                self.symbol_table.declare(
                    var_name,
                    {
                        "type_qual": type_qual,
                        "datatype": datatype_copy,
                        "name": var_name,
                        "addr": addr,
                        "size": size,
                        "frame_kind": frame_kind,
                        **({"val": initial_val} if initial_val is not None else {}),
                    },
                    scope=self.current_scope,
                )
            case _:
                throw_error(alloc)

    def _declare_input_builtin(self):
        if self.symbol_table.contains("input", scope="global"):
            return
        self.symbol_table.declare(
            "input",
            {
                "datatype": pn.FunDecl([], pn.IntType(), pn.Name("input"), []),
                "name": "input",
                "param_size": 0,
            },
            scope="global",
        )

    def _declare_print_builtin(self):
        if self.symbol_table.contains("print", scope="global"):
            return
        self.symbol_table.declare(
            "print",
            {
                "datatype": pn.FunDecl([], pn.VoidType(), pn.Name("print"), []),
                "name": "print",
                "param_size": 0,
            },
            scope="global",
        )

    def _function_pointer_datatype(self, fun_decl):
        match fun_decl:
            case pn.FunDecl(_, ret_dt, _, params):
                return pn.FunPtrDecl(copy.deepcopy(ret_dt), copy.deepcopy(params))
            case _:
                throw_error(fun_decl)

    def _resolve_name_to_storage(self, name_node):
        match name_node:
            case pn.Name(var_name):
                symbol, chosen_scope = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                if symbol is None:
                    throw_error(
                        f"Use of undeclared identifier '{var_name}' in scope '{self.current_scope}'"
                    )
                match symbol.get("datatype"):
                    case pn.FunDecl() as fun_decl:
                        return pn.FunRef(
                            copy.deepcopy(name_node),
                            self._function_pointer_datatype(fun_decl),
                        )
                    case None:
                        throw_error(
                            f"Internal error: symbol '{var_name}' has no datatype"
                        )
                    case _:
                        pass
                match symbol.get("type_qual"):
                    case pn.Const():
                        return copy.deepcopy(symbol.get("val", name_node))
                    case pn.Writeable():
                        if chosen_scope == "global":
                            loc = pn.Global(copy.deepcopy(name_node))
                        else:
                            match symbol["frame_kind"]:
                                case "param":
                                    loc = pn.StackframeParam(pn.Num(symbol["addr"]))
                                case "local_var":
                                    loc = pn.StackframeLocalVar(pn.Num(symbol["addr"]))
                                case frame_kind:
                                    throw_error(
                                        f"Internal error: unsupported frame kind for '{var_name}': {frame_kind!r}"
                                    )
                            loc.symbol_name = var_name
                        return loc
                    case type_qual:
                        throw_error(
                            f"Internal error: unsupported type qualifier for '{var_name}': {type_qual!r}"
                        )
            case _:
                throw_error(
                    f"Internal error: expected Name while resolving storage, got {name_node!r}"
                )

    def _picoc_rewrite_exp(self, exp):
        match exp:
            case pn.Name():
                return self._resolve_name_to_storage(exp)
            case pn.Num() | pn.Char() | pn.Empty() | pn.Stack():
                return exp
            case pn.StackframeLocalVar() | pn.StackframeParam() | pn.Global():
                return exp
            case pn.BinOp(left_exp, bin_op, right_exp):
                return pn.BinOp(
                    self._picoc_rewrite_exp(left_exp),
                    bin_op,
                    self._picoc_rewrite_exp(right_exp),
                )
            case pn.UnOp(un_op, inner_exp):
                return pn.UnOp(un_op, self._picoc_rewrite_exp(inner_exp))
            case pn.PostInc(inner_exp):
                return pn.PostInc(self._picoc_rewrite_exp(inner_exp))
            case pn.PostDec(inner_exp):
                return pn.PostDec(self._picoc_rewrite_exp(inner_exp))
            case pn.Cast(datatype, exp):
                return pn.Cast(datatype, self._picoc_rewrite_exp(exp))
            case pn.ToBool(inner_exp):
                return pn.ToBool(self._picoc_rewrite_exp(inner_exp))
            case pn.Atom(left_exp, rel, right_exp):
                return pn.Atom(
                    self._picoc_rewrite_exp(left_exp),
                    rel,
                    self._picoc_rewrite_exp(right_exp),
                )
            case pn.Ref(inner):
                return pn.Ref(self._picoc_rewrite_exp(inner))
            case pn.Deref(inner):
                return pn.Deref(self._picoc_rewrite_exp(inner))
            # case pn.Subscr(ref, idx):
            #     return pn.Subscr(
            #         self._rewrite_names_exp(ref),
            #         self._rewrite_names_exp(idx),
            #     )
            case pn.Attr(inner_exp, pn.Name() as attr_name):
                return pn.Attr(self._picoc_rewrite_exp(inner_exp), attr_name)
            case pn.Array(exps):
                return pn.Array([self._picoc_rewrite_exp(inner) for inner in exps])
            case pn.Struct(init_pairs):
                init_pairs_out = []
                for init_pair in init_pairs:
                    match init_pair:
                        case pn.InitPair(lhs, inner_exp):
                            init_pairs_out.append(
                                pn.InitPair(lhs, self._picoc_rewrite_exp(inner_exp))
                            )
                        case _:
                            throw_error(init_pair)
                return pn.Struct(init_pairs_out)
            case pn.Call(pn.Name() as fun_name, exps):
                if fun_name.val == "input":
                    self._declare_input_builtin()
                    return pn.Call(
                        fun_name, [self._picoc_rewrite_exp(inner) for inner in exps]
                    )
                elif fun_name.val == "print":
                    self._declare_print_builtin()
                    return pn.Call(
                        fun_name, [self._picoc_rewrite_exp(inner) for inner in exps]
                    )
                symbol, _ = self.symbol_table.resolve(fun_name.val, scope="global")
                if isinstance(symbol, dict) and isinstance(
                    symbol.get("datatype"), pn.FunDecl
                ):
                    return pn.Call(
                        fun_name, [self._picoc_rewrite_exp(inner) for inner in exps]
                    )
                return pn.Call(
                    self._picoc_rewrite_exp(fun_name),
                    [self._picoc_rewrite_exp(inner) for inner in exps],
                )
            case pn.Call(fun_exp, exps):
                return pn.Call(
                    self._picoc_rewrite_exp(fun_exp),
                    [self._picoc_rewrite_exp(inner) for inner in exps],
                )
            case pn.Asm():
                return exp
            case pn.SizeOf():
                return exp
            case pn.Exit():
                return exp
            case pn.Alloc():
                return exp
            case _:
                throw_error(exp)

    def _picoc_rewrite_stmt(self, stmt):
        match stmt:
            case pn.Assign(pn.Alloc() as alloc, exp):
                return pn.Assign(alloc, self._picoc_rewrite_exp(exp))
            case pn.Assign(lhs, exp):
                return pn.Assign(
                    self._picoc_rewrite_exp(lhs), self._picoc_rewrite_exp(exp)
                )
            case pn.Exp(exp):
                return pn.Exp(self._picoc_rewrite_exp(exp))
            case pn.If(exp, stmts):
                return pn.If(
                    self._picoc_rewrite_exp(exp),
                    [self._picoc_rewrite_stmt(inner) for inner in stmts],
                )
            case pn.IfElse(exp, stmts1, stmts2):
                return pn.IfElse(
                    self._picoc_rewrite_exp(exp),
                    [self._picoc_rewrite_stmt(inner) for inner in stmts1],
                    [self._picoc_rewrite_stmt(inner) for inner in stmts2],
                )
            case pn.While(exp, stmts):
                return pn.While(
                    self._picoc_rewrite_exp(exp),
                    [self._picoc_rewrite_stmt(inner) for inner in stmts],
                )
            case pn.DoWhile(exp, stmts):
                return pn.DoWhile(
                    self._picoc_rewrite_exp(exp),
                    [self._picoc_rewrite_stmt(inner) for inner in stmts],
                )
            case pn.Return(pn.Empty()):
                return stmt
            case pn.Return(exp):
                return pn.Return(self._picoc_rewrite_exp(exp))
            case pn.GoTo():
                return stmt
            # ---------------------------- L_Misc -----------------------------
            case pn.SingleLineComment() | pn.Debug():
                return stmt
            case _:
                throw_error(stmt)

    def _picoc_symbol_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1)), num
            ):
                self._declare_alloc(
                    pn.Alloc(type_qual, datatype, pn.Name(val1)),
                    initial_val=copy.deepcopy(num),
                )
                return self._single_line_comment(stmt, "//")
            case pn.Assign(pn.Alloc(type_qual, _, pn.Name() as name) as alloc, exp):
                initial_val = (
                    copy.deepcopy(exp) if isinstance(type_qual, pn.Const) else None
                )
                self._declare_alloc(alloc, initial_val=initial_val)
                new_stmt = pn.Assign(name, exp)
                return self._single_line_comment(stmt, "//") + [new_stmt]
            case pn.Exp(pn.Alloc() as alloc):
                self._declare_alloc(alloc)
                return self._single_line_comment(stmt, "//")
            case pn.Assign():
                return [stmt]
            case pn.Exp():
                return [stmt]
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_symbol_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            case pn.IfElse(exp, stmts1, stmts2):
                new_stmts1 = []
                for inner_stmt in stmts1:
                    new_stmts1 += self._picoc_symbol_stmt(inner_stmt)
                new_stmts2 = []
                for inner_stmt in stmts2:
                    new_stmts2 += self._picoc_symbol_stmt(inner_stmt)
                stmt.stmts1 = new_stmts1
                stmt.stmts2 = new_stmts2
                return [stmt]
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_symbol_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            case pn.DoWhile(exp, stmts):
                new_stmts = []
                for inner_stmt in stmts:
                    new_stmts += self._picoc_symbol_stmt(inner_stmt)
                stmt.stmts = new_stmts
                return [stmt]
            # ----------------------------- L_Fun -----------------------------
            case pn.Return(exp):
                return [stmt]
            case pn.GoTo():
                return [stmt]
            # ---------------------------- L_Misc -----------------------------
            case pn.SingleLineComment() | pn.Debug():
                return [stmt]
            case _:
                throw_error(stmt)

    def _picoc_symbol_decl_def(self, decl_def):
        match decl_def:
            case pn.StructSpec(pn.Name(struct_name)):
                existing, _ = self.symbol_table.resolve(
                    struct_name, scope=self.current_scope
                )
                if existing is not None and existing.get("complete", True):
                    return []
                self.symbol_table.declare(
                    struct_name,
                    {
                        "type_qual": pn.Empty(),
                        "datatype": decl_def,
                        "name": struct_name,
                        "attrs": [],
                        "size": pn.Empty(),
                        "complete": False,
                    },
                    scope=self.current_scope,
                )
                return []
            case pn.StructDecl(pn.Name(struct_name), allocs):
                attrs = []
                struct_size = 0
                for alloc in allocs:
                    match alloc:
                        case pn.Alloc(pn.Writeable(), datatype, pn.Name(attr_name)):
                            attr_size = self._datatype_size(datatype)
                            self.symbol_table.declare(
                                attr_name,
                                {
                                    "type_qual": pn.Empty(),
                                    "datatype": datatype,
                                    "name": attr_name,
                                    "addr": pn.Empty(),
                                    "size": attr_size,
                                },
                                scope=struct_name,
                            )
                            attrs += [pn.Name(attr_name)]
                            struct_size += attr_size
                        case _:
                            throw_error(alloc)

                self.symbol_table.declare(
                    struct_name,
                    {
                        "type_qual": pn.Empty(),
                        "datatype": decl_def,
                        "name": struct_name,
                        "attrs": attrs,
                        "size": struct_size,
                        "complete": True,
                    },
                    scope=self.current_scope,
                )
                return []
            case pn.FunDecl(_, datatype, pn.Name(fun_name), allocs):
                param_size = self._param_size(allocs)
                self.symbol_table.declare(
                    fun_name,
                    {
                        "datatype": decl_def,
                        "name": fun_name,
                        "param_size": param_size,
                        "variadic": self._is_variadic_params(allocs),
                    },
                    scope="global",
                )
                return []
            case pn.FunDef(_, datatype, pn.Name(fun_name) as name, allocs, blocks):
                fun_blocks_out = []
                self.current_scope = fun_name
                self.symbol_table.set_parent(fun_name, "global")
                self.next_param_addr = 0
                self.next_local_addr = 0

                param_size = self._param_size(allocs)
                if not self.symbol_table.contains(fun_name, scope="global"):
                    self.symbol_table.declare(
                        fun_name,
                        {
                            "datatype": pn.FunDecl([], datatype, name, allocs),
                            "name": fun_name,
                            "param_size": param_size,
                            "variadic": self._is_variadic_params(allocs),
                        },
                        scope="global",
                    )

                for alloc in self._fixed_params(allocs):
                    self._declare_alloc(alloc, is_param=True)

                for block in blocks:
                    match block:
                        case pn.Block(_, stmts_instrs):
                            rewritten_stmts_instrs = []
                            for stmt in stmts_instrs:
                                # Needed for cases like `int x = expr;`, where
                                # `_picoc_symbol_stmt` expands one source statement into
                                # multiple nodes. Its output feeds `_picoc_rewrite_stmt`, so
                                # without this the origin chain would break at `inner`
                                typed_out = self._inherit_origin_many(
                                    self._picoc_symbol_stmt(stmt), stmt
                                )
                                rewritten_stmts_instrs += [
                                    self._inherit_origin(self._picoc_rewrite_stmt(inner), inner)
                                    for inner in typed_out
                                ]
                            block.stmts_instrs = rewritten_stmts_instrs
                            fun_blocks_out.append(block)
                            self.block_scopes[block.name] = fun_name
                        case _:
                            throw_error(block)

                match fun_blocks_out:
                    case [pn.Block(_, entry_stmts), *_]:
                        # Symbol pass knows the final local-frame size after declaring locals,
                        # so NewStackframe is inserted here instead of in ANF.
                        entry_stmts[:0] = [
                            self._inherit_origin(
                                pn.NewStackframe(pn.Num(str(self.next_local_addr))),
                                decl_def,
                            )
                        ]
                    case _:
                        throw_error(fun_blocks_out)

                match blocks[-1]:
                    case pn.Block(_, stmts) if stmts and isinstance(
                        stmts[-1], pn.Return
                    ):
                        pass
                    case pn.Block(_, stmts):
                        stmts.append(pn.Return())
                    case _:
                        throw_error(blocks[-1])

                self.fun_local_sizes[fun_name] = self.next_local_addr
                self.current_scope = "global"
                return fun_blocks_out
            case pn.Exp() | pn.Assign():
                self.current_scope = "global"
                rewritten = self._inherit_origin_many(
                    self._picoc_symbol_stmt(decl_def), decl_def
                )
                rewritten = [self._inherit_origin(self._picoc_rewrite_stmt(stmt), stmt) for stmt in rewritten]
                self.global_decl_stmts += copy.deepcopy(rewritten)
                return []
            case _:
                throw_error(decl_def)

    def picoc_symbol(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(_, decls_defs_blocks):
                self.current_scope = "global"
                # reset accumulators for repeated runs
                self.global_decl_stmts = []
                self.fun_local_sizes = {}
                self.block_scopes = {}
                fun_blocks_out = []
                for decl_def in decls_defs_blocks:
                    fun_blocks_out += self._picoc_symbol_decl_def(decl_def)

                blocks_out = [
                    pn.Block("_global_inits", self.global_decl_stmts)
                ] + fun_blocks_out
                self.block_scopes["_global_inits"] = "global"
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_symbol"),
                    blocks_out,
                )
            case _:
                throw_error(file)
