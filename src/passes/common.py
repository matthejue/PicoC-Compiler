from src.passes.dependencies import *


class PassStateMixin:
    def __init__(self):
        # PicoC_Blocks
        self.block_idx = 0
        self.all_blocks = dict()
        # PicoC_ANF
        self.argmode_on = False
        self.symbol_table = SymbolTable()
        self.current_scope = "global"
        self.global_stmts_instrs = []
        self.next_param_addr = 0
        self.next_local_addr = 0
        self.stack_type_hints = {}
        self.fun_local_sizes = {}
        self.global_decl_stmts = []
        self.block_scopes = {}

        self.generated_string_literals = {}
        self.generated_string_defs = []
        self.generated_string_counter = 0
        self.inline_functions = {}

        # RETI_Blocks
        self.instrs_cnt = 0

    INT32_MIN = -2147483648
    INT32_MAX = 2147483647

    def _inherit_origin(self, target, source):
        return copy_source_origin(target, source)

    def _inherit_origin_many(self, targets, source):
        return copy_source_origin_to_many(targets, source)

    def _is_static_inline(self, node):
        specifiers = getattr(node, "storage_class_specifiers", [])
        # C allows both orders: static inline and inline static.
        if specifiers == [pn.Inline()]:
            throw_error("'inline' functions without 'static' are not supported")
        return specifiers in ([pn.Static(), pn.Inline()], [pn.Inline(), pn.Static()])

    def _collect_inline_functions(self, decls_defs):
        self.inline_functions = {}
        for decl_def in decls_defs:
            match decl_def:
                case pn.FunDef(_, _, pn.Name(fun_name), allocs, stmts):
                    if not self._is_static_inline(decl_def):
                        continue
                    match stmts:
                        # Excludes variadic functions like f(int x, ...);
                        # the simple inliner only substitutes named params.
                        case [pn.Return(exp)] if (
                            not isinstance(exp, pn.Empty)
                            and all(isinstance(alloc, pn.Alloc) for alloc in allocs)
                        ):
                            self.inline_functions[fun_name] = {
                                "allocs": allocs,
                                "return_exp": exp,
                            }
                        case _:
                            pass

    def _inline_static_call(self, fun_name, exps):
        inline_fun = self.inline_functions.get(fun_name)
        if inline_fun is None:
            return None

        allocs = inline_fun["allocs"]
        replacements = {}
        for alloc, exp in zip(allocs, exps):
            match alloc:
                case pn.Alloc(_, _, pn.Name(param_name)):
                    replacements[param_name] = exp
                case _:
                    return None

        return self._replace_inline_params(inline_fun["return_exp"], replacements)

    def _replace_inline_params(self, node, replacements):
        match node:
            # Handles return arg; directly, and Name attributes reached while
            # walking a bigger return expression like return arg + 1;.
            case pn.Name(val) if val in replacements:
                return copy.deepcopy(replacements[val])
            # Handles list attributes reached while walking an AST node, e.g.
            # the argument list in Call(..., exps).
            case list():
                return [self._replace_inline_params(elem, replacements) for elem in node]
            # Walk a compound expression node, e.g. BinOp(left, op, right). Its
            # attributes are passed back into this function and may hit cases above.
            case pn.ASTNode():
                node_copy = copy.deepcopy(node)
                for key, value in vars(node_copy).items():
                    setattr(node_copy, key, self._replace_inline_params(value, replacements))
                return node_copy
            case _:
                return copy.deepcopy(node)

    def _should_omit_inlined_fun_def(self, decl_def):
        match decl_def:
            case pn.FunDef(_, _, pn.Name(fun_name), _, _):
                return fun_name in self.inline_functions
        return False

    def _is_variadic_params(self, allocs) -> bool:
        return bool(allocs) and isinstance(allocs[-1], pn.VariadicParam)

    def _fixed_params(self, allocs):
        return [alloc for alloc in allocs if not isinstance(alloc, pn.VariadicParam)]

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
        return pn.Array([pn.Char(ch) for ch in literal.val] + [pn.Char("\\0")])

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
            pn.Num(str(len(literal.val) + 1)),
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
                        return (
                            pn.ArrayDecl(
                                pn.Num(str(len(literal.val) + 1)),
                                copy.deepcopy(inner_dt),
                            ),
                            self._string_literal_to_array(literal),
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

