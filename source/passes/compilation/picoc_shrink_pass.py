from source import global_vars
from source import picoc_nodes as pn
from source.utils.util_funs_dependent import throw_error
import copy


class PicocShrinkPass:
    INT32_MIN = -2147483648
    INT32_MAX = 2147483647

    def _is_static_inline(self, node):
        specifiers = getattr(node, "storage_class_specifiers", [])
        return specifiers in ([pn.Static(), pn.Inline()], [pn.Inline(), pn.Static()])

    def _has_no_params(self, allocs):
        return not allocs or (len(allocs) == 1 and isinstance(allocs[0], pn.VoidType))

    def _is_asm_only_function(self, stmts):
        return bool(stmts) and all(
            isinstance(stmt, pn.Exp)
            and isinstance(stmt.exp, pn.Asm)
            and isinstance(stmt.exp.code, pn.String)
            for stmt in stmts
        )

    def _collect_static_asm_inline_functions(self, decls_defs):
        self.static_asm_inline_functions = {}
        for decl_def in decls_defs:
            match decl_def:
                case pn.FunDef(_, _, pn.Name(fun_name), allocs, stmts, _):
                    if not (
                        self._is_static_inline(decl_def)
                        and self._is_asm_only_function(stmts)
                    ):
                        continue
                    if not self._has_no_params(allocs):
                        throw_error("static inline asm functions with parameters are not supported")
                    self.static_asm_inline_functions[fun_name] = stmts
                case _:
                    pass

    def _inline_static_asm_call(self, stmt):
        match stmt:
            case pn.Exp(pn.Call(pn.Name(fun_name), exps)):
                inline_stmts = self.static_asm_inline_functions.get(fun_name)
                if inline_stmts is None:
                    return None
                if exps:
                    throw_error("static inline asm functions with arguments are not supported")
                return copy.deepcopy(inline_stmts)
        return None

    def _should_omit_static_asm_inline_fun_def(self, decl_def):
        match decl_def:
            case pn.FunDef(_, _, pn.Name(fun_name), _, _, _):
                return fun_name in self.static_asm_inline_functions
        return False

    def _fits_int32(self, val: int) -> bool:
        return self.INT32_MIN <= val <= self.INT32_MAX

    def _const_int_value(self, exp):
        match exp:
            case pn.Num(val):
                return int(val, 0)
            case pn.Char(val):
                return self._char_literal_code(val)
            case pn.ToBool(inner_exp):
                inner_val = self._const_int_value(inner_exp)
                if inner_val is None or not self._fits_int32(inner_val):
                    return None
                return 1 if inner_val != 0 else 0
        return None

    def _c_div(self, left_val: int, right_val: int):
        if right_val == 0:
            return None
        sign = -1 if (left_val < 0) ^ (right_val < 0) else 1
        return sign * (abs(left_val) // abs(right_val))

    def _c_mod(self, left_val: int, right_val: int):
        div = self._c_div(left_val, right_val)
        if div is None:
            return None
        return left_val - div * right_val

    def _fold_binop_const(self, bin_op, left_val: int, right_val: int):
        if not (self._fits_int32(left_val) and self._fits_int32(right_val)):
            return None
        match bin_op:
            case pn.Add():
                res = left_val + right_val
            case pn.Sub():
                res = left_val - right_val
            case pn.Mul():
                res = left_val * right_val
            case pn.Div():
                res = self._c_div(left_val, right_val)
            case pn.Mod():
                res = self._c_mod(left_val, right_val)
            case pn.Oplus():
                res = left_val ^ right_val
            case pn.And():
                res = left_val & right_val
            case pn.Or():
                res = left_val | right_val
            case pn.LogicAnd():
                res = 1 if (left_val != 0 and right_val != 0) else 0
            case pn.LogicOr():
                res = 1 if (left_val != 0 or right_val != 0) else 0
            case _:
                return None
        if res is None or not self._fits_int32(res):
            return None
        return res

    def _fold_atom_const(self, rel, left_val: int, right_val: int):
        if not (self._fits_int32(left_val) and self._fits_int32(right_val)):
            return None
        match rel:
            case pn.Eq():
                res = left_val == right_val
            case pn.NEq():
                res = left_val != right_val
            case pn.Lt():
                res = left_val < right_val
            case pn.Gt():
                res = left_val > right_val
            case pn.LtE():
                res = left_val <= right_val
            case pn.GtE():
                res = left_val >= right_val
            case _:
                return None
        return 1 if res else 0

    def _string_literal_to_array(self, literal: pn.String):
        characters = []
        index = 0

        while index < len(literal.val):
            character = literal.val[index]

            if character == "\\" and index + 1 < len(literal.val):
                characters.append(pn.Char(literal.val[index : index + 2]))
                index += 2
            else:
                characters.append(pn.Char(character))
                index += 1

        return pn.Array(characters + [pn.Char("\\0")])

    def _globalize_string_literal(self, literal: pn.String):
        cached_name = self.generated_string_literals.get(literal.val)
        if cached_name is not None:
            return pn.Name(cached_name)

        # Create a unique compiler-internal global name for the lifted string literal.
        symbol_name = f"__strlit_{self.generated_string_counter}"
        self.generated_string_counter += 1
        self.generated_string_literals[literal.val] = symbol_name

        array_exp = self._string_literal_to_array(literal)
        array_dt = pn.ArrayDecl(
            pn.Num(str(len(array_exp.exps))),
            pn.CharType(),
        )
        self.generated_string_defs.append(
            self._inherit_origin(
                pn.Assign(
                    pn.Alloc(pn.Writeable(), array_dt, pn.Name(symbol_name)),
                    array_exp,
                ),
                literal,
            )
        )
        return pn.Name(symbol_name)

    def _infer_unsized_array_size_from_initializer(self, datatype, initializer):
        match datatype:
            case pn.ArrayDecl(pn.Empty(), inner_dt):
                match initializer:
                    case pn.String() as literal:
                        array_exp = self._string_literal_to_array(literal)
                        return (
                            pn.ArrayDecl(
                                pn.Num(str(len(array_exp.exps))),
                                copy.deepcopy(inner_dt),
                            ),
                            array_exp,
                        )
                    case pn.Array(exps):
                        return (
                            pn.ArrayDecl(
                                pn.Num(str(len(exps))),
                                copy.deepcopy(inner_dt),
                            ),
                            initializer,
                        )
                    case _:
                        throw_error(
                            "Array declarations with omitted size require a valid initializer"
                        )
            case _:
                return datatype, initializer

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
            case pn.Alloc(type_qual, datatype, name, local_var_or_param, section):
                if isinstance(datatype, pn.ArrayDecl) and isinstance(datatype.const_exp, pn.Empty):
                    throw_error(
                        "Array declarations with omitted size require a valid initializer"
                    )
                alloc = pn.Alloc(
                    type_qual,
                    self._picoc_shrink_datatype(datatype),
                    name,
                    section=section,
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
            case pn.FunDecl(_, ret_dt, name, allocs, section):
                if allocs and isinstance(allocs[0], pn.VoidType):
                    allocs_shrunk = []
                else:
                    allocs_shrunk = [
                        self._picoc_shrink_exp(a)
                        if not isinstance(a, pn.VariadicParam)
                        else a
                        for a in allocs
                    ]
                return pn.FunDecl([], ret_dt, name, allocs_shrunk, section=section)
            case pn.StructSpec() | pn.IntType() | pn.CharType() | pn.VoidType():
                return datatype
            case _:
                return datatype

    def _picoc_shrink_stmt(self, stmt):
        match stmt:
            case pn.Typedef(datatype, name):
                return pn.Typedef(self._picoc_shrink_datatype(datatype), name)
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(pn.Alloc(type_qual, datatype, name, _, section), exp):
                # char str[] = "..." becomes a regular array and can be put on the stack.
                datatype, exp = self._infer_unsized_array_size_from_initializer(datatype, exp)
                return pn.Assign(
                    pn.Alloc(
                        type_qual,
                        self._picoc_shrink_datatype(datatype),
                        name,
                        section=section,
                    ),
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
                    stmts_shrinked += self._picoc_shrink_stmt_many(stmt)
                return pn.If(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked,
                )
            case pn.IfElse(exp, stmts1, stmts2):
                stmts_shrinked1 = []
                for stmt1 in stmts1:
                    stmts_shrinked1 += self._picoc_shrink_stmt_many(stmt1)
                stmts_shrinked2 = []
                for stmt2 in stmts2:
                    stmts_shrinked2 += self._picoc_shrink_stmt_many(stmt2)
                return pn.IfElse(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked1,
                    stmts_shrinked2,
                )
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += self._picoc_shrink_stmt_many(stmt)
                return pn.While(
                    self._inherit_origin(self._picoc_shrink_exp(exp), exp),
                    stmts_shrinked,
                )
            case pn.DoWhile(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += self._picoc_shrink_stmt_many(stmt)
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

    def _picoc_shrink_stmt_many(self, stmt):
        inline_stmts = self._inline_static_asm_call(stmt)
        if inline_stmts is not None:
            return self._inherit_origin_many(
                [self._picoc_shrink_stmt(inline_stmt) for inline_stmt in inline_stmts],
                stmt,
            )
        return [self._inherit_origin(self._picoc_shrink_stmt(stmt), stmt)]

    def picoc_shrink(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                filename = val
                self.generated_string_literals = {}
                self.generated_string_defs = []
                self.generated_string_counter = 0
                self._collect_static_asm_inline_functions(decls_defs)
                decls_defs_shrinked = []
                for decl_def in decls_defs:
                    if self._should_omit_static_asm_inline_fun_def(decl_def):
                        continue
                    match decl_def:
                        case pn.Typedef(datatype, name):
                            decls_defs_shrinked.append(
                                pn.Typedef(self._picoc_shrink_datatype(datatype), name)
                            )
                        case pn.StructSpec() as structspec:
                            decls_defs_shrinked += [structspec]
                        case pn.FunDef(storage_class_specifiers, datatype, pn.Name() as name, allocs, stmts, section):
                            naked = getattr(decl_def, "naked", False)
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
                                stmts_shrinked += self._picoc_shrink_stmt_many(stmt)
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
                                section,
                                naked=naked,
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
                        case pn.FunDecl(storage_class_specifiers, datatype, pn.Name() as name, allocs, section):
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
                                    section=section,
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
