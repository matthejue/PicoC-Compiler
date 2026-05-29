from src import global_vars
from src import picoc_nodes as pn
from src.utils.util_funs_dependent import throw_error


class PicocShrinkPass:
    # =========================================================================
    # =                              PicoC_Shrink                             =
    # =========================================================================
    # - Ersetzt Array-Zugriffe durch Pointer-Arithmetik (arr[i] -> *(arr + i))

    def _picoc_shrink_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name():
                return exp
            case pn.Num():
                return exp
            case pn.Char():
                return exp
            case pn.String():
                # char *str = "..." always points to generated global data.
                return self._globalize_string_literal(exp)
            case pn.BinOp(left_exp, bin_op, right_exp):
                left_shrunk = self._picoc_shrink_exp(left_exp)
                right_shrunk = self._picoc_shrink_exp(right_exp)
                left_val = self._const_int_value(left_shrunk)
                right_val = self._const_int_value(right_shrunk)
                if left_val is not None and right_val is not None:
                    folded = self._fold_binop_const(bin_op, left_val, right_val)
                    if folded is not None:
                        return pn.Num(str(folded))
                return pn.BinOp(left_shrunk, bin_op, right_shrunk)
            case pn.UnOp(un_op, exp):
                return pn.UnOp(un_op, self._picoc_shrink_exp(exp))
            case pn.PostInc(exp):
                return pn.PostInc(self._picoc_shrink_exp(exp))
            case pn.PostDec(exp):
                return pn.PostDec(self._picoc_shrink_exp(exp))
            case pn.Cast(datatype, exp):
                return pn.Cast(datatype, self._picoc_shrink_exp(exp))
            case pn.SizeOf():
                return exp
            case pn.Asm():
                return exp
            # ---------------------------- L_Logic ----------------------------
            case pn.Atom(left_exp, rel, right_exp):
                left_shrunk = self._picoc_shrink_exp(left_exp)
                right_shrunk = self._picoc_shrink_exp(right_exp)
                left_val = self._const_int_value(left_shrunk)
                right_val = self._const_int_value(right_shrunk)
                if left_val is not None and right_val is not None:
                    folded = self._fold_atom_const(rel, left_val, right_val)
                    if folded is not None:
                        return pn.Num(str(folded))
                return pn.Atom(left_shrunk, rel, right_shrunk)
            case pn.ToBool(exp):
                return pn.ToBool(self._picoc_shrink_exp(exp))
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Alloc(type_qual, datatype, name, local_var_or_param):
                if isinstance(datatype, pn.ArrayDecl) and isinstance(datatype.const_exp, pn.Empty):
                    throw_error(
                        "Array declarations with omitted size require a valid initializer"
                    )
                alloc = pn.Alloc(
                    type_qual,
                    self._picoc_shrink_datatype(datatype),
                    name,
                )
                alloc.local_var_or_param = local_var_or_param
                return alloc
            # ----------------------------- L_Pntr ----------------------------
            case pn.Deref(inner):
                inner_shrunk = self._picoc_shrink_exp(inner)
                match inner_shrunk:
                    # *&x (optionally with offset) -> x (or x with offset)
                    case pn.BinOp(pn.Ref(inner_ref), pn.Add() | pn.Sub() as bin_op, pn.Num("0")):
                        return inner_ref
                    case pn.BinOp(pn.Ref(inner_ref), pn.Add() | pn.Sub() as bin_op, offset_exp):
                        return pn.BinOp(inner_ref, bin_op, offset_exp)
                return pn.Deref(inner_shrunk)
            case pn.Ref(ref):
                ref_shrunk = self._picoc_shrink_exp(ref)
                match ref_shrunk:
                    # &( *(addr) ) cancels to addr
                    case pn.Deref(pn.BinOp(addr_exp, pn.Add() | pn.Sub() as bin_op, pn.Num("0"))):
                        return addr_exp
                    case pn.Deref(pn.BinOp(addr_exp, pn.Add() | pn.Sub() as bin_op, offset_exp)):
                        return pn.BinOp(addr_exp, bin_op, offset_exp)
                    case pn.Deref(addr_exp):
                        return addr_exp
                return pn.Ref(ref_shrunk)
            # ---------------------------- L_Array ----------------------------
            case pn.Subscr(ref, exp):
                ref_shrunk = self._picoc_shrink_exp(ref)
                exp_shrunk = self._picoc_shrink_exp(exp)
                return pn.Deref(pn.BinOp(ref_shrunk, pn.Add(), exp_shrunk))
            case pn.Array(exps):
                return pn.Array([self._picoc_shrink_exp(exp) for exp in exps])
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(ref, name):
                return pn.Attr(self._picoc_shrink_exp(ref), name)
            case pn.Struct(init_pairs):
                init_pairs_shrinked = []
                for init_pair in init_pairs:
                    match init_pair:
                        case pn.InitPair(lhs, exp):
                            init_pairs_shrinked += [
                                pn.InitPair(
                                    lhs,
                                    self._picoc_shrink_exp(exp),
                                )
                            ]
                        case _:
                            throw_error(init_pairs)
                return pn.Struct(init_pairs_shrinked)
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(fun_exp, exps):
                if isinstance(fun_exp, pn.Name):
                    inline_exp = self._inline_static_call(fun_exp.val, exps)
                    if inline_exp is not None:
                        return self._picoc_shrink_exp(inline_exp)
                return pn.Call(
                    self._picoc_shrink_exp(fun_exp),
                    [self._picoc_shrink_exp(exp) for exp in exps],
                )
            case _:
                throw_error(exp)

    def _picoc_shrink_datatype(self, datatype):
        match datatype:
            case pn.ArrayDecl(const_exp, inner_dt):
                const_shrunk = self._picoc_shrink_exp(const_exp)
                return pn.ArrayDecl(const_shrunk, self._picoc_shrink_datatype(inner_dt))
            case pn.PntrDecl(inner_dt):
                return pn.PntrDecl(self._picoc_shrink_datatype(inner_dt))
            case pn.FunPtrDecl(ret_dt, params):
                if isinstance(ret_dt, pn.StructSpec):
                    throw_error(
                        "Returning structs by value is not supported; use "
                        "a pointer to the struct instead. If a function returns "
                        "a struct, the usual trick is to rewrite it so the caller "
                        "creates the struct in its own stackframe and passes a "
                        "struct pointer to the function"
                    )
                params_shrunk = []
                for param in params:
                    match param:
                        case pn.ParamDecl(type_qual, param_dt):
                            params_shrunk.append(
                                pn.ParamDecl(
                                    type_qual,
                                    self._picoc_shrink_datatype(param_dt),
                                )
                            )
                        case pn.VoidType() | pn.VariadicParam():
                            params_shrunk.append(param)
                            break
                        case pn.Alloc():
                            throw_error(
                                "Named parameters in function pointer declarations are "
                                "not supported; use unnamed parameter types instead, "
                                "e.g. 'int (*fp)(int, char);' instead of "
                                "'int (*fp)(int x, char y);'"
                            )
                        case _:
                            throw_error(param)
                return pn.FunPtrDecl(self._picoc_shrink_datatype(ret_dt), params_shrunk)
            case pn.FunDecl(_, ret_dt, name, allocs):
                if allocs and isinstance(allocs[0], pn.VoidType):
                    allocs_shrunk = []
                else:
                    allocs_shrunk = [
                        self._picoc_shrink_exp(a)
                        if not isinstance(a, pn.VariadicParam)
                        else a
                        for a in allocs
                    ]
                return pn.FunDecl([], ret_dt, name, allocs_shrunk)
            case pn.StructSpec() | pn.IntType() | pn.CharType() | pn.VoidType():
                return datatype
            case _:
                return datatype

    def _picoc_shrink_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(pn.Alloc(type_qual, datatype, name), exp):
                # char str[] = "..." becomes a regular array and can be put on the stack.
                datatype, exp = self._infer_unsized_array_size_from_initializer(datatype, exp)
                return pn.Assign(
                    pn.Alloc(type_qual, self._picoc_shrink_datatype(datatype), name),
                    self._picoc_shrink_exp(exp),
                )
            case pn.Assign(lhs, exp):
                return pn.Assign(
                    self._picoc_shrink_exp(lhs), self._picoc_shrink_exp(exp)
                )
            case pn.StructSpec() | pn.StructDecl():
                throw_error(
                    "Struct declarations and forward declarations inside function "
                    "definitions are not supported. Move the struct declaration "
                    "or forward declaration to global scope."
                )
            case pn.Exp(exp):
                return pn.Exp(self._picoc_shrink_exp(exp))
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._inherit_origin(self._picoc_shrink_stmt(stmt), stmt)]
                return pn.If(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked,
                )
            case pn.IfElse(exp, stmts1, stmts2):
                stmts_shrinked1 = []
                for stmt1 in stmts1:
                    stmts_shrinked1 += [self._inherit_origin(self._picoc_shrink_stmt(stmt1), stmt1)]
                stmts_shrinked2 = []
                for stmt2 in stmts2:
                    stmts_shrinked2 += [self._inherit_origin(self._picoc_shrink_stmt(stmt2), stmt2)]
                return pn.IfElse(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked1,
                    stmts_shrinked2,
                )
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._inherit_origin(self._picoc_shrink_stmt(stmt), stmt)]
                return pn.While(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked,
                )
            case pn.DoWhile(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._inherit_origin(self._picoc_shrink_stmt(stmt), stmt)]
                return pn.DoWhile(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked,
                )
            # ----------------------------- L_Fun -----------------------------
            case pn.Return(pn.Empty()):
                return stmt
            case pn.Return(exp):
                return pn.Return(self._picoc_shrink_exp(exp))
            # ---------------------------- L_Misc -----------------------------
            case pn.Debug():
                return stmt
            case _:
                throw_error(stmt)

    def picoc_shrink(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                filename = val
                self.generated_string_literals = {}
                self.generated_string_defs = []
                self.generated_string_counter = 0
                self._collect_inline_functions(decls_defs)
                decls_defs_shrinked = []
                for decl_def in decls_defs:
                    if self._should_omit_inlined_fun_def(decl_def):
                        continue
                    match decl_def:
                        case pn.StructSpec() as structspec:
                            decls_defs_shrinked += [structspec]
                        case pn.FunDef(storage_class_specifiers, datatype, pn.Name() as name, allocs, stmts):
                            if isinstance(datatype, pn.StructSpec):
                                throw_error(
                                    "Returning structs by value is not supported; use "
                                    "a pointer to the struct instead. If a function returns "
                                    "a struct, the usual trick is to rewrite it so the caller "
                                    "creates the struct in its own stackframe and passes a "
                                    "struct pointer to the function"
                                )
                            stmts_shrinked = []
                            for stmt in stmts:
                                stmts_shrinked += [self._inherit_origin(self._picoc_shrink_stmt(stmt), stmt)]
                            if allocs and isinstance(allocs[0], pn.VoidType):
                                allocs_shrinked = []
                            else:
                                allocs_shrinked = [
                                    self._picoc_shrink_exp(alloc)
                                    if not isinstance(alloc, pn.VariadicParam)
                                    else alloc
                                    for alloc in allocs
                                ]
                            fun_def = pn.FunDef(
                                storage_class_specifiers,
                                datatype,
                                name,
                                allocs_shrinked,
                                stmts_shrinked,
                            )
                            decls_defs_shrinked += [
                                self._inherit_origin(fun_def, decl_def)
                            ]
                        case pn.StructDecl(pn.Name() as name, allocs):
                            allocs_shrinked = [
                                self._picoc_shrink_exp(alloc) for alloc in allocs
                            ]
                            decls_defs_shrinked += [
                                pn.StructDecl(name, allocs_shrinked)
                            ]
                        case pn.FunDecl(storage_class_specifiers, datatype, pn.Name() as name, allocs):
                            if isinstance(datatype, pn.StructSpec):
                                throw_error(
                                    "Returning structs by value is not supported; use "
                                    "a pointer to the struct instead. If a function returns "
                                    "a struct, the usual trick is to rewrite it so the caller "
                                    "creates the struct in its own stackframe and passes a "
                                    "struct pointer to the function"
                                )
                            if any(isinstance(alloc, pn.ParamDecl) for alloc in allocs):
                                throw_error(
                                    "Unnamed parameters in function declarations are not "
                                    "supported; use named parameters instead, e.g. "
                                    "'int f(int x);' instead of 'int f(int);'"
                                )
                            if allocs and isinstance(allocs[0], pn.VoidType):
                                allocs_shrinked = []
                            else:
                                allocs_shrinked = [
                                    self._picoc_shrink_exp(alloc)
                                    if not isinstance(alloc, pn.VariadicParam)
                                    else alloc
                                    for alloc in allocs
                                ]
                            decls_defs_shrinked += [
                                pn.FunDecl(
                                    storage_class_specifiers,
                                    datatype,
                                    name,
                                    allocs_shrinked,
                                )
                            ]
                        case pn.Exp() | pn.Assign():
                            decls_defs_shrinked += [
                                self._inherit_origin(self._picoc_shrink_stmt(decl_def), decl_def)
                            ]
                        case _:
                            throw_error(decl_def)
                decls_defs_shrinked = self.generated_string_defs + decls_defs_shrinked
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_shrink"),
                    decls_defs_shrinked,
                )
            case _:
                throw_error(file)
