from src import picoc_nodes as pn
from src import reti_nodes as rn
from src import debug as db
from src.symbol_table import SymbolTable
from src.utils.util_funs_dependent import throw_error
from src.utils.util_funs_independent import (
    convert_to_single_line,
)
from src import global_vars
import copy
from bitstring import Bits
from inspect import isclass
import sys


class Passes:
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

        # RETI_Blocks
        self.instrs_cnt = 0

    INT32_MIN = -2147483648
    INT32_MAX = 2147483647

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
            pn.Assign(
                pn.Alloc(pn.Writeable(), array_dt, pn.Name(symbol_name)),
                array_exp,
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
            case pn.Call(name, exps):
                return pn.Call(name, [self._picoc_shrink_exp(exp) for exp in exps])
            case _:
                throw_error(exp)

    def _picoc_shrink_datatype(self, datatype):
        match datatype:
            case pn.ArrayDecl(const_exp, inner_dt):
                const_shrunk = self._picoc_shrink_exp(const_exp)
                return pn.ArrayDecl(const_shrunk, self._picoc_shrink_datatype(inner_dt))
            case pn.PntrDecl(inner_dt):
                return pn.PntrDecl(self._picoc_shrink_datatype(inner_dt))
            case pn.FunDecl(ret_dt, name, allocs):
                if allocs and isinstance(allocs[0], pn.VoidType):
                    allocs_shrunk = []
                else:
                    allocs_shrunk = [
                        self._picoc_shrink_exp(a)
                        if not isinstance(a, pn.VariadicParam)
                        else a
                        for a in allocs
                    ]
                return pn.FunDecl(ret_dt, name, allocs_shrunk)
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
            case pn.Exp(exp):
                return pn.Exp(self._picoc_shrink_exp(exp))
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
                return pn.If(self._picoc_shrink_exp(exp), stmts_shrinked)
            case pn.IfElse(exp, stmts1, stmts2):
                stmts_shrinked1 = []
                for stmt1 in stmts1:
                    stmts_shrinked1 += [self._picoc_shrink_stmt(stmt1)]
                stmts_shrinked2 = []
                for stmt2 in stmts2:
                    stmts_shrinked2 += [self._picoc_shrink_stmt(stmt2)]
                return pn.IfElse(
                    self._picoc_shrink_exp(exp), stmts_shrinked1, stmts_shrinked2
                )
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
                return pn.While(self._picoc_shrink_exp(exp), stmts_shrinked)
            case pn.DoWhile(exp, stmts):
                stmts_shrinked = []
                for stmt in stmts:
                    stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
                return pn.DoWhile(self._picoc_shrink_exp(exp), stmts_shrinked)
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
                decls_defs_shrinked = []
                for decl_def in decls_defs:
                    match decl_def:
                        case pn.FunDef(datatype, pn.Name() as name, allocs, stmts):
                            stmts_shrinked = []
                            for stmt in stmts:
                                stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
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
                                pn.FunDef(
                                    datatype,
                                    name,
                                    allocs_shrinked,
                                    stmts_shrinked,
                                )
                            ]
                        case pn.StructDecl(pn.Name() as name, allocs):
                            allocs_shrinked = [
                                self._picoc_shrink_exp(alloc) for alloc in allocs
                            ]
                            decls_defs_shrinked += [
                                pn.StructDecl(name, allocs_shrinked)
                            ]
                        case pn.FunDecl(datatype, pn.Name() as name, allocs):
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
                                    datatype,
                                    name,
                                    allocs_shrinked,
                                )
                            ]
                        case pn.Exp() | pn.Assign():
                            decls_defs_shrinked += [
                                self._picoc_shrink_stmt(decl_def)
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

    # =========================================================================
    # =                              PicoC_Blocks                             =
    # =========================================================================
    # -  If(exp, stmts), IfElse(exp, stmts1, stmts2), While(exp, stmts) und
    # DoWhile(exp, stmts) durch Block(name, stmts instrs-, GoTo(lable)- und
    # IfElse(exp, stmts1, stmts2) ersetzt.

    IMPORTANT_STMTS_INSTRS = [
        pn.Ref,
        #  pn.Assign,
        pn.Assign(pn.Stack, pn.Global),
        pn.Assign(pn.Stack, pn.Stackframe),
        pn.Assign(pn.Global, pn.Stack),
        pn.Assign(pn.Stackframe, pn.Stack),
        pn.Assign(pn.Name, object),
        pn.Assign(pn.Attr, object),
        pn.Assign(pn.Deref, object),
        pn.Assign(pn.Stack, pn.Stack),
        #  pn.Exp,
        pn.Exp(pn.Num),
        pn.Exp(pn.Name),
        pn.Exp(pn.BinOp),
        pn.Exp(pn.Stack),
        pn.Exp(pn.Global),
        pn.Exp(pn.Stackframe),
        pn.Exp(pn.Deref),
        pn.Exp(pn.Attr),
        pn.Exp(pn.Deref),
        pn.Exp(pn.Ref),
        pn.Exp(pn.GoTo),
        pn.Exp(rn.Reg),
        pn.StackMalloc,
        pn.NewStackframe,
        pn.RemoveStackframe,
        pn.Return,
        pn.Exit,
        pn.If,
        pn.IfElse,
        pn.While,
        pn.DoWhile,
        pn.StackMalloc,
    ]

    def _single_line_comment(self, node, prefix, filtr=[1, 2, 3]):
        if not (global_vars.args.verbose or global_vars.args.double_verbose):
            return []
        if global_vars.args.example:
            for stmt_instr in self.IMPORTANT_STMTS_INSTRS:
                if isclass(stmt_instr):
                    if isinstance(node, stmt_instr):
                        break  # success
                else:
                    if type(node) is type(stmt_instr):
                        for i in range(len(stmt_instr.visible)):
                            if not isinstance(node.visible[i], stmt_instr.visible[i]):
                                break
                        else:
                            break  # success
            else:
                return []
        if hasattr(node, "visible"):
            for i, visible_list_item in enumerate(node.visible):
                if isinstance(visible_list_item, list) and i in filtr:
                    node.visible[i] = []
        return [pn.SingleLineComment(prefix, convert_to_single_line(node))]

    def _char_literal_code(self, val: str) -> int:
        if len(val) == 2 and val[0] == "\\":
            escape_map = {
                "0": 0,
                "n": 10,
                "t": 9,
                "r": 13,
                "\\": 92,
                "'": 39,
                '"': 34,
            }
            return escape_map.get(val[1], ord(val[1]))
        return ord(val)

    # def _single_line_comment(self, node, prefix, filtr=[1, 2, 3]):
    #     if not (global_vars.args.verbose or global_vars.args.double_verbose):
    #         return []
    #     if global_vars.args.example:
    #         for stmt_instr in self.IMPORTANT_STMTS_INSTRS:
    #             if isclass(stmt_instr):
    #                 if isinstance(node, stmt_instr):
    #                     break  # success
    #             else:
    #                 if type(node) is type(stmt_instr):
    #                     for i in range(len(stmt_instr.visible)):
    #                         if not isinstance(node.visible[i], stmt_instr.visible[i]):
    #                             break
    #                     else:
    #                         break  # success
    #         else:
    #             return []
    #
    #     def _repr_with_visible(node_for_repr, visible):
    #         if not visible:
    #             return f"\n{node_for_repr.__class__.__name__}()"
    #         parts = []
    #         for child in visible:
    #             match child:
    #                 case list() as lst:
    #                     if not lst:
    #                         parts.append("[]")
    #                     else:
    #                         lst_parts = []
    #                         for item in lst:
    #                             try:
    #                                 lst_parts.append(convert_to_single_line(item))
    #                             except Exception:
    #                                 lst_parts.append(repr(item))
    #                         parts.append("[" + ", ".join(lst_parts) + "]")
    #                 case str() as s:
    #                     parts.append(f"'{s}'")
    #                 case int() as i:
    #                     parts.append(str(i))
    #                 case _:
    #                     try:
    #                         parts.append(child.__repr__())
    #                     except Exception:
    #                         parts.append(repr(child))
    #         return f"\n{node_for_repr.__class__.__name__}(" + ", ".join(parts) + ")"
    #
    #     if hasattr(node, "visible"):
    #         visible_copy = copy.deepcopy(list(node.visible))
    #         for i, visible_list_item in enumerate(visible_copy):
    #             if isinstance(visible_list_item, list) and i in filtr:
    #                 visible_copy[i] = []
    #         node_repr = _repr_with_visible(node, visible_copy)
    #         return [pn.SingleLineComment(prefix, convert_to_single_line(node_repr))]
    #
    #     return [pn.SingleLineComment(prefix, convert_to_single_line(node))]

    def _create_block(self, labelbase, stmts, blocks, *, add_id=True):
        label = labelbase + (f".{self.block_idx}" if add_id else "")
        new_block = pn.Block(
            label,
            stmts,
        )
        new_block.block_idx = self.block_idx
        blocks[label] = new_block
        self.block_idx += 1
        return pn.GoTo(pn.Name(label))

    def _picoc_blocks_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_if = [goto_after]
                for sub_stmt in reversed(stmts):
                    stmts_if = self._picoc_blocks_stmt(sub_stmt, stmts_if, blocks)
                goto_if = self._create_block("if", stmts_if, blocks)

                return self._single_line_comment(stmt, "//") + [
                    pn.IfElse(exp, [goto_if], [goto_after])
                ]
            case pn.IfElse(exp, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._picoc_blocks_stmt(stmt, stmts_else, blocks)
                goto_else = self._create_block("else", stmts_else, blocks)

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_blocks_stmt(stmt, stmts_if, blocks)
                goto_if = self._create_block("if", stmts_if, blocks)

                return self._single_line_comment(stmt, "//") + [
                    pn.IfElse(exp, [goto_if], [goto_else])
                ]
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = pn.GoTo(pn.Name("placeholder"))
                goto_condition_check = pn.GoTo(pn.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for sub_stmt in reversed(stmts):
                    stmts_while = self._picoc_blocks_stmt(sub_stmt, stmts_while, blocks)
                goto_branch.name.val = self._create_block(
                    "while_branch", stmts_while, blocks
                ).name.val

                condition_check = [pn.IfElse(exp, [goto_branch], [goto_after])]
                goto_condition_check.name.val = self._create_block(
                    "condition_check", condition_check, blocks
                ).name.val

                return self._single_line_comment(stmt, "//") + [goto_condition_check]
            case pn.DoWhile(exp, stmts):
                goto_after = self._create_block(
                    "do_while_after", processed_stmts, blocks
                )

                goto_branch = pn.GoTo(pn.Name("placeholder"))
                stmts_while = [pn.IfElse(exp, [goto_branch], [goto_after])]

                for sub_stmt in reversed(stmts):
                    stmts_while = self._picoc_blocks_stmt(sub_stmt, stmts_while, blocks)
                goto_branch.name.val = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).name.val

                return self._single_line_comment(stmt, "//") + [goto_branch]
            # ----------------------------- L_Fun -----------------------------
            case pn.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_blocks_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case pn.FunDef(datatype, pn.Name(val) as name, allocs, stmts):
                fun_name = val
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_blocks_stmt(
                        stmt, processed_stmts, blocks
                    )

                self._create_block(fun_name, processed_stmts, blocks, add_id=False)
                self.all_blocks |= blocks
                return [
                    pn.FunDef(
                        datatype,
                        name,
                        allocs,
                        list(
                            sorted(
                                blocks.values(),
                                key=lambda block: -int(block.block_idx),
                            )
                        ),
                    )
                ]
            case pn.FunDecl() | pn.StructDecl() | pn.Exp() | pn.Assign():
                return [decl_def]
            case _:
                throw_error(decl_def)

    def picoc_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += self._picoc_blocks_def(decl_def)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_blocks"),
                    decls_defs_blocks,
                )
            case _:
                throw_error(file)

    # =========================================================================
    # =                            PicoC_Symbol                               =
    # =========================================================================
    # - builds the symbol table and rewrites PicoC Name nodes ahead of typing
    # - decalres function and struct declarations and defintions to symbol table

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
            case pn.IntType() | pn.CharType() | pn.PntrDecl():
                return 1
            # ---------------------------- L_Struct ---------------------------
            case pn.StructSpec(pn.Name(val)):
                struct_type_name = val
                symbol, _ = self.symbol_table.resolve(
                    struct_type_name, scope=self.current_scope
                )
                return int(symbol["size"])
            # ---------------------------- L_Array ----------------------------
            case pn.ArrayDecl(pn.Num(val), datatype2):
                elem_size = self._datatype_size(datatype2)
                return elem_size * int(val)
            case _:
                throw_error(datatype)

    def _declare_alloc(self, alloc, *, initial_val=None):
        match alloc:
            case pn.VoidType():
                return
            case pn.Alloc(type_qual, datatype, pn.Name(val1), local_var_or_param):
                var_name = val1
                datatype_copy = copy.deepcopy(datatype)
                # Parameters of array type decay to pointers to their first element type.
                if local_var_or_param == "param" and isinstance(
                    datatype_copy, pn.ArrayDecl
                ):
                    datatype_copy = self._ref_result_datatype(datatype_copy.datatype)

                size = self._datatype_size(datatype_copy)
                match self.current_scope:
                    case "global":
                        addr = pn.Empty()
                        frame_kind = "global"
                    case _:
                        match local_var_or_param:
                            case "param":
                                addr = self.next_param_addr + size - 1
                                self.next_param_addr += size
                                frame_kind = "param"
                            case _:
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

    def _stackframe_access_offset(self, addr, frame_kind, tmp_idx=0):
        addr = int(addr)
        tmp_idx = int(tmp_idx)
        match frame_kind:
            case "param":
                return 1 + addr - tmp_idx
            case "local_var":
                return -(2 + addr - tmp_idx)
            case _:
                raise ValueError(f"Unknown frame kind: {frame_kind}")

    def _declare_input_builtin(self):
        if self.symbol_table.contains("input", scope="global"):
            return
        self.symbol_table.declare(
            "input",
            {
                "datatype": pn.FunDecl(pn.IntType(), pn.Name("input"), []),
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
                "datatype": pn.FunDecl(pn.VoidType(), pn.Name("print"), []),
                "name": "print",
                "param_size": 0,
            },
            scope="global",
        )

    def _resolve_name_to_storage(self, name_node):
        match name_node:
            case pn.Name(var_name):
                symbol, chosen_scope = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                # TODO: error message instead
                if symbol is None:
                    return name_node
                match symbol.get("type_qual"):
                    case pn.Const():
                        return copy.deepcopy(symbol.get("val", name_node))
                    case _:
                        if chosen_scope == "global":
                            loc = pn.Global(copy.deepcopy(name_node))
                        else:
                            loc = pn.Stackframe(pn.Num(symbol["addr"]))
                            loc.symbol_name = var_name
                            loc.frame_kind = symbol["frame_kind"]
                        return loc
            case _:
                return name_node

    def _picoc_rewrite_exp(self, exp):
        match exp:
            case pn.Name():
                return self._resolve_name_to_storage(exp)
            case pn.Num() | pn.Char() | pn.Empty() | pn.Stack():
                return exp
            case pn.Stackframe() | pn.Global():
                return exp
            case pn.BinOp(left_exp, bin_op, right_exp):
                return pn.BinOp(
                    self._picoc_rewrite_exp(left_exp),
                    bin_op,
                    self._picoc_rewrite_exp(right_exp),
                )
            case pn.UnOp(un_op, inner_exp):
                return pn.UnOp(un_op, self._picoc_rewrite_exp(inner_exp))
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
                elif fun_name.val == "print":
                    self._declare_print_builtin()
                return pn.Call(
                    fun_name, [self._picoc_rewrite_exp(inner) for inner in exps]
                )
            case pn.Asm():
                return exp
            # case pn.Call(fun_exp, exps):
            #     return pn.Call(
            #         self._picoc_rewrite_exp(fun_exp),
            #         [self._picoc_rewrite_exp(inner) for inner in exps],
            #     )
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
            case pn.StackMalloc() | pn.NewStackframe() | pn.RemoveStackframe():
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
                return [stmt]  # self._single_line_comment(stmt, "//")
            case pn.Assign(pn.Alloc(type_qual, _, pn.Name() as name) as alloc, exp):
                initial_val = (
                    copy.deepcopy(exp) if isinstance(type_qual, pn.Const) else None
                )
                self._declare_alloc(alloc, initial_val=initial_val)
                new_stmt = pn.Assign(name, exp)
                # return self._single_line_comment(stmt, "//") + self._picoc_symbol_stmt(new_stmt)
                return self._picoc_symbol_stmt(new_stmt)
            case pn.Exp(pn.Alloc() as alloc):
                self._declare_alloc(alloc)
                # return self._single_line_comment(stmt, "//")
                return [stmt]
            case pn.Assign(lhs, exp):
                return [pn.Assign(lhs, exp)]
            case pn.Exp(exp):
                return [pn.Exp(exp)]
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
            case pn.StackMalloc() | pn.NewStackframe() | pn.RemoveStackframe():
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
                    },
                    scope=self.current_scope,
                )
                return []
            case pn.FunDecl(datatype, pn.Name(fun_name), allocs):
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
            case pn.FunDef(datatype, pn.Name(fun_name) as name, allocs, blocks):
                fun_blocks_out = []
                self.current_scope = fun_name
                self.symbol_table.set_parent(fun_name, "global")
                self.next_param_addr = 0
                self.next_local_addr = 0

                if fun_name not in ["main", "global"]:
                    for alloc in self._fixed_params(allocs):
                        alloc.local_var_or_param = "param"

                param_size = self._param_size(allocs)
                if not self.symbol_table.contains(fun_name, scope="global"):
                    self.symbol_table.declare(
                        fun_name,
                        {
                            "datatype": pn.FunDecl(datatype, name, allocs),
                            "name": fun_name,
                            "param_size": param_size,
                            "variadic": self._is_variadic_params(allocs),
                        },
                        scope="global",
                    )

                for alloc in self._fixed_params(allocs):
                    self._declare_alloc(alloc)

                for block in blocks:
                    match block:
                        case pn.Block(_, stmts_instrs):
                            self.stack_type_hints = {}
                            rewritten_stmts_instrs = []
                            for stmt in stmts_instrs:
                                typed_out = self._picoc_symbol_stmt(stmt)
                                rewritten_stmts_instrs += [
                                    self._picoc_rewrite_stmt(inner)
                                    for inner in typed_out
                                ]
                            block.stmts_instrs = rewritten_stmts_instrs
                            fun_blocks_out.append(block)
                            self.block_scopes[block.name] = fun_name
                        case _:
                            throw_error(block)

                match blocks:
                    case [pn.Block(_, entry_stmts), *_]:
                        entry_stmts[:0] = [
                            pn.Exp(alloc)
                            for alloc in self._fixed_params(allocs)
                            if not isinstance(alloc, pn.VoidType)
                        ]
                        entry_stmts[:0] = [
                            pn.StackMalloc(self.next_local_addr)
                        ]
                        # entry_stmts[:0] = (
                        #     self._single_line_comment(blocks[0], "//", filtr=[2])
                        #     if global_vars.args.double_verbose
                        #     else []
                        # ) + [pn.StackMalloc(self.next_local_addr)]
                    case _:
                        throw_error(blocks)

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
                rewritten = self._picoc_symbol_stmt(decl_def)
                rewritten = [self._picoc_rewrite_stmt(stmt) for stmt in rewritten]
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

    # =========================================================================
    # =                            PicoC_Typing                               =
    # =========================================================================
    # - annotates the PicoC AST with datatype information collected

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

    def _attr_result_datatype(self, struct_dt, attr_name: str):
        match struct_dt:
            case pn.StructSpec(pn.Name(struct_name)):
                symbol, _ = self.symbol_table.resolve(attr_name, scope=struct_name)
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
                    case {"datatype": pn.FunDecl(ret_dt, _, _)}:
                        exp.datatype = copy.deepcopy(ret_dt)
                        return copy.deepcopy(ret_dt)
                    case _:
                        throw_error(symbol)
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
            case pn.Exp(pn.Alloc()):
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

    # =========================================================================
    # =                               PicoC_ANF                               =
    # =========================================================================
    # - bringt AST in A-Normalform:

    def _picoc_anf_exp(self, exp, addr_calc=False):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case (pn.Global() | pn.Stackframe()) as loc:
                datatype = loc.datatype
                if addr_calc:
                    match datatype:
                        case pn.StructSpec() | pn.ArrayDecl() | pn.PntrDecl() | pn.IntType() | pn.CharType():
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
                        case pn.PntrDecl() | pn.IntType() | pn.CharType():
                            return [pn.Exp(loc)]
                        case _:
                            throw_error(datatype)
            case pn.Num() | pn.Char():
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
                    (pn.IntType, pn.CharType, pn.VoidType, pn.StructSpec, pn.ArrayDecl, pn.PntrDecl),
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
            case pn.Call(pn.Name(val) as name, exps):
                fun_name = val
                symbol, _ = self.symbol_table.resolve(fun_name, scope="global")
                datatype = symbol["datatype"]
                match datatype:
                    case pn.FunDecl(datatype2, pn.Name()):
                        return_type = datatype2
                    case _:
                        throw_error(datatype)

                exps_anf = []
                self.argmode_on = True
                for exp2 in reversed(exps):
                    exps_anf += self._picoc_anf_exp(exp2)
                self.argmode_on = False

                return (
                    self._single_line_comment(exp, "//", filtr=[])
                    + exps_anf
                    + [
                        pn.NewStackframe(pn.Num(str(len(exps)))),
                        pn.Exp(pn.GoTo(pn.Name(fun_name))),
                        pn.RemoveStackframe(
                            pn.Num(str(self.next_local_addr))
                        ),
                    ]
                    + (
                        [pn.Exp(rn.Reg(rn.Acc()))]
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
                self._picoc_anf_exp(alloc)
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
                return self._single_line_comment(stmt, "//") + stmt_anf
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
            case pn.Assign(pn.Stackframe() as lhs, exp):
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
                        target = pn.Stackframe(pn.Num(addr))
                        setattr(
                            target, "symbol_name", getattr(lhs, "symbol_name", None)
                        )
                        setattr(target, "datatype", getattr(lhs, "datatype", None))
                        setattr(target, "frame_kind", symbol["frame_kind"])
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
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1)), num
            ):
                # Symbol table already populated during typing; no runtime code needed
                return self._single_line_comment(stmt, "//") + []
            case pn.Assign(pn.Alloc(_, _, name) as alloc, exp):
                self._picoc_anf_exp(alloc)
                stmt_anf = self._picoc_anf_stmt(
                        pn.Assign(self._picoc_rewrite_exp(name), exp) # TODO: ist Name bereits Stackframe oder Global?
                )
                return self._single_line_comment(stmt, "//") + stmt_anf
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
            case pn.StackMalloc():
                return [stmt]
            case pn.Return(pn.Empty()):
                return [stmt]
            case pn.Return(exp):
                exps_anf = self._picoc_anf_exp(exp)
                return (
                    self._single_line_comment(stmt, "//")
                    + exps_anf
                    + [pn.Return(pn.Stack(pn.Num("1")))]
                )
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
                for block in blocks:
                    label = block.name
                    self.current_scope = self.block_scopes.get(label, "global")
                    self.next_local_addr = self.fun_local_sizes.get(self.current_scope, 0)
                    match block:
                        case pn.Block(_, stmts):
                            stmts_anf = []
                            for stmt in stmts:
                                stmts_anf += self._picoc_anf_stmt(stmt)
                            block.stmts_instrs[:] = stmts_anf
                            blocks_anf.append(block)
                        case _:
                            throw_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_anf"),
                    blocks_anf,
                )
            case _:
                throw_error(file)

    # =========================================================================
    # =                              RETI_Blocks                              =
    # =========================================================================
    # - PicoC-Knoten werden durch semantisch entsprechende RETI-Knoten ersetzt

    def _reti_blocks_stmt(self, stmt):
        match stmt:
            # --------------------------- L_Comment ---------------------------
            case pn.SingleLineComment(prefix, content):
                match prefix:
                    case "//":
                        return [pn.SingleLineComment("# //", content)]
                    #  case "// //":
                    #      return [pn.SingleLineComment("# // //", content)]
                    case _:
                        throw_error(prefix)
            # ---------------------------- L_Logic ----------------------------
            case pn.Exp(
                pn.BinOp(
                    pn.Stack(pn.Num(val1)),
                    (pn.LogicAnd() | pn.LogicOr()) as bin_lop,
                    pn.Stack(pn.Num(val2)),
                )
            ):
                match bin_lop:
                    case pn.LogicAnd():
                        lop = rn.And()
                    case pn.LogicOr():
                        lop = rn.Or()
                    case _:
                        throw_error(bin_lop)
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val1)]
                    ),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)]
                    ),
                    rn.Instr(lop, [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
            case pn.Exp(pn.UnOp(pn.LogicNot(), pn.Stack(pn.Num(val)))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Oplus(), [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            # ---------------------------- L_Arith ----------------------------
            case pn.Exp((pn.Num() | pn.Char() | rn.Reg()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                match exp:
                    case pn.Num(val):
                        reti_instrs += [
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)])
                        ]
                    case pn.Char(val):
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadi(),
                                [rn.Reg(rn.Acc()), rn.Im(str(self._char_literal_code(val)))],
                            )
                        ]
                    case rn.Reg():
                        return reti_instrs + [
                            rn.Instr(rn.Storein(), [rn.Reg(rn.Sp()), exp, rn.Im("1")]),
                        ]
                    case _:
                        throw_error(exp)

                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            case pn.Exp((pn.Global() | pn.Stackframe()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                match exp:
                    case pn.Global(pn.Name(val2)):
                        name = rn.Name(val2)
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Ds()), rn.Reg(rn.Acc()), name],
                            ),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                            ),
                        ]
                    case pn.Stackframe(pn.Num(val2)):
                        frame_kind = getattr(exp, "frame_kind", None)
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Baf()),
                                    rn.Reg(rn.Acc()),
                                    rn.Im(
                                        str(
                                            self._stackframe_access_offset(
                                                val2, frame_kind
                                            )
                                        )
                                    ),
                                ],
                            ),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                            ),
                        ]
                return reti_instrs
            case pn.Ref((pn.Global() | pn.Stackframe()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                match exp:
                    case pn.Global(pn.Name(val)):
                        name = rn.Name(val)
                        reti_instrs += [
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.In1()), name]),
                            rn.Instr(rn.Add(), [rn.Reg(rn.In1()), rn.Reg(rn.Ds())]),
                        ]
                    case pn.Stackframe(pn.Num(val)):
                        frame_kind = getattr(exp, "frame_kind", None)
                        reti_instrs += [
                            rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.In1())]),
                            rn.Instr(
                                rn.Addi() if frame_kind == "param" else rn.Subi(),
                                [
                                    rn.Reg(rn.In1()),
                                    rn.Im(
                                        str(
                                            abs(
                                                self._stackframe_access_offset(
                                                    val, frame_kind
                                                )
                                            )
                                        )
                                    ),
                                ],
                            ),
                        ]
                    case _:
                        throw_error(exp)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")],
                    )
                ]
            case pn.Exp(
                pn.BinOp(pn.Stack(pn.Num(val1)), bin_aop, pn.Stack(pn.Num(val2)))
            ):
                match (
                    stmt.exp.left_exp.datatype,
                    bin_aop,
                    stmt.exp.right_exp.datatype,
                ):
                    case (
                        pn.PntrDecl(inner_dt) | pn.ArrayDecl(_, inner_dt),
                        pn.Sub(),
                        pn.PntrDecl(_) | pn.ArrayDecl(_, _),
                    ):
                        reti_instrs = self._single_line_comment(stmt, "#")
                        help_const = self._datatype_size(inner_dt)
                        return reti_instrs + [
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Sp()),
                                    rn.Reg(rn.Acc()),
                                    rn.Im(val1),
                                ],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Sp()),
                                    rn.Reg(rn.In2()),
                                    rn.Im(val2),
                                ],
                            ),
                            rn.Instr(
                                rn.Sub(),
                                [rn.Reg(rn.Acc()), rn.Reg(rn.In2())],
                            ),
                            rn.Instr(
                                rn.Divi(),
                                [rn.Reg(rn.Acc()), rn.Im(str(help_const))],
                            ),
                            rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                            ),
                        ]
                    case (
                        pn.PntrDecl(inner_dt) | pn.ArrayDecl(_, inner_dt),
                        pn.Add() | pn.Sub(),
                        _,
                    ) | (
                        _,
                        pn.Add() | pn.Sub(),
                        pn.PntrDecl(inner_dt) | pn.ArrayDecl(_, inner_dt),
                    ):
                        reti_instrs = self._single_line_comment(stmt, "#")
                        help_const = self._datatype_size(inner_dt)
                        match bin_aop:
                            case pn.Add():
                                aop = rn.Add()
                            case pn.Sub():
                                aop = rn.Sub()
                            case _:
                                throw_error(bin_aop)
                        return reti_instrs + [
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Sp()),
                                    rn.Reg(rn.In1()),
                                    rn.Im(val1),
                                ],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Sp()),
                                    rn.Reg(rn.In2()),
                                    rn.Im(val2),
                                ],
                            ),
                            rn.Instr(
                                rn.Multi(),
                                [rn.Reg(rn.In2()), rn.Im(str(help_const))],
                            ),
                            rn.Instr(aop, [rn.Reg(rn.In1()), rn.Reg(rn.In2())]),
                            rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")],
                            ),
                        ]
                    case (pn.StructSpec() | pn.IntType() | pn.CharType(), _, _) | (
                        _,
                        _,
                        pn.StructSpec() | pn.IntType() | pn.CharType(),
                    ):
                        match bin_aop:
                            case pn.Add():
                                aop = rn.Add()
                            case pn.Sub():
                                aop = rn.Sub()
                            case pn.Mul():
                                aop = rn.Mult()
                            case pn.Div():
                                aop = rn.Div()
                            case pn.Mod():
                                aop = rn.Mod()
                            case pn.Oplus():
                                aop = rn.Oplus()
                            case pn.And():
                                aop = rn.And()
                            case pn.Or():
                                aop = rn.Or()
                            case _:
                                throw_error(bin_aop)
                        return self._single_line_comment(stmt, "#") + [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val1)],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)],
                            ),
                            rn.Instr(aop, [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")],
                            ),
                            rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                        ]
                    case _:
                        throw_error(
                            stmt.exp.left_exp.datatype,
                            bin_aop,
                            stmt.exp.right_exp.datatype,
                        )
            case pn.Exp(pn.UnOp(un_op, pn.Stack(pn.Num(val)))):
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("0")]),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Sub(), [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                ]
                match un_op:
                    case pn.Not():
                        reti_instrs += [
                            rn.Instr(rn.Subi(), [rn.Reg(rn.Acc()), rn.Im("1")])
                        ]
                    case pn.Minus():
                        pass
                    case _:
                        throw_error(un_op)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    )
                ]
            case pn.Exp(pn.Call(pn.Name("input"), [])):
                return self._single_line_comment(stmt, "#") + [
                    # rn.Call(rn.Name("INPUT"), rn.Reg(rn.Acc())),
                    rn.Int(rn.Im("2")),
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            case pn.Exp(pn.Call(pn.Name("print"), [pn.Stack(pn.Num(val))])):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Int(rn.Im("0")),
                ]
            case pn.Exp(pn.Asm(pn.String(code))):
                return self._single_line_comment(stmt, "#") + [rn.RawInstr(code.strip())]
            case pn.Exp(pn.Cast(_, pn.Stack())):
                return self._single_line_comment(stmt, "# // cast no-op")
            case pn.Exp(pn.Debug()):
                return self._single_line_comment(stmt, "#") + [
                    rn.Int(rn.Im("3")),
                ]
            case pn.Exit(pn.Num(val)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)]),
                    rn.Jump(rn.Always(), rn.Im("0")),
                ]
            case pn.Exp(pn.SizeOf(val)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            # ---------------------------- L_Logic ----------------------------
            case pn.Exp(pn.ToBool(pn.Stack(pn.Num(val)))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Jump(rn.Eq(), rn.Im("3")),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                ]
            case pn.Exp(pn.Atom(pn.Stack(pn.Num(val1)), rel, pn.Stack(pn.Num(val2)))):
                match rel:
                    case pn.Eq():
                        rel = rn.Eq()
                    case pn.NEq():
                        rel = rn.NEq()
                    case pn.Lt():
                        rel = rn.Lt()
                    case pn.LtE():
                        rel = rn.LtE()
                    case pn.Gt():
                        rel = rn.Gt()
                    case pn.GtE():
                        rel = rn.GtE()
                    case _:
                        throw_error(rel)
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val1)]
                    ),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)]
                    ),
                    rn.Instr(rn.Sub(), [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                    rn.Jump(rel, rn.Im("3")),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("0")]),
                    rn.Jump(rn.Always(), rn.Im("2")),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(
                pn.Stack(pn.Num(val1)) as lhs,
                (pn.Global() | pn.Stackframe()) as exp,
            ):
                tmp_max = lhs.num.val
                tmp = pn.Stack(pn.Num(0))
                mem = copy.deepcopy(exp)
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(val1)])
                ]
                while True:
                    match (tmp, mem):
                        case (pn.Stack(pn.Num(val)), _) if val == tmp_max:
                            break
                        case (pn.Stack(pn.Num(val1)), pn.Global(pn.Name(val2))):
                            name = rn.Name(val2)
                            constant = int(val1)  # TODO: Int not needed?
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Ds()),
                                        rn.Reg(rn.Acc()),
                                        # rn.Im(str(int(val2) + int(val1))),
                                        (
                                            name
                                            if constant == 0
                                            else rn.BinOp(name, rn.Add(), constant)
                                        ),
                                    ],
                                ),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        rn.Reg(rn.Sp()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(int(val1) + 1)),
                                    ],
                                ),
                            ]
                        case (pn.Stack(pn.Num(val1)), pn.Stackframe(pn.Num(val2))):
                            frame_kind = getattr(mem, "frame_kind", None)
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Baf()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(
                                            str(
                                                self._stackframe_access_offset(
                                                    val2, frame_kind, val1
                                                )
                                            )
                                        ),
                                    ],
                                ),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        rn.Reg(rn.Sp()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(int(val1) + 1)),
                                    ],
                                ),
                            ]
                    tmp.num.val = str(int(tmp.num.val) + 1)
                return reti_instrs
            case pn.Assign(
                (pn.Global() | pn.Stackframe()) as lhs,
                pn.Stack(pn.Num(val2)) as tmp,
            ):
                tmp_max = tmp.num.val
                mem = copy.deepcopy(lhs)
                tmp = pn.Stack(pn.Num(0))
                reti_instrs = []
                stack_offset = val2
                reti_instrs = self._single_line_comment(stmt, "#")
                while True:
                    match (mem, tmp):
                        case (_, pn.Stack(pn.Num(val))) if val == tmp_max:
                            break
                        case (pn.Global(pn.Name(val1)), pn.Stack(pn.Num(val2))):
                            name = rn.Name(val1)
                            constant = int(tmp_max) - 1 - int(val2)
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Sp()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(int(val2) + 1)),
                                    ],
                                ),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        rn.Reg(rn.Ds()),
                                        rn.Reg(rn.Acc()),
                                        # rn.Im(
                                        #     str(
                                        #         int(val1) + int(tmp_max) - 1 - int(val2)
                                        #     )
                                        (
                                            name
                                            if constant == 0
                                            else rn.BinOp(name, rn.Add(), constant)
                                        ),
                                    ],
                                ),
                            ]
                        case (pn.Stackframe(pn.Num(val1)), pn.Stack(pn.Num(val2))):
                            frame_kind = getattr(mem, "frame_kind", None)
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Sp()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(int(val2) + 1)),
                                    ],
                                ),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        rn.Reg(rn.Baf()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(
                                            str(
                                                self._stackframe_access_offset(
                                                    val1,
                                                    frame_kind,
                                                    int(tmp_max) - 1 - int(val2),
                                                )
                                            )
                                        ),
                                    ],
                                ),
                            ]
                        case _:
                            throw_error((mem, tmp))
                    tmp.num.val = int(tmp.num.val) + 1
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im(stack_offset)])
                ]
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Exp(pn.Deref(pn.Stack(pn.Num(val1), datatype))):
                match datatype:
                    case pn.StructSpec() | pn.PntrDecl() | pn.IntType() | pn.CharType():
                        return self._single_line_comment(stmt, "#") + [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.In1()), rn.Reg(rn.Acc()), rn.Im("0")],
                            ),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                            ),
                        ]
                    case pn.ArrayDecl():
                        return self._single_line_comment(stmt, "# // not included")
                    case _:
                        throw_error(datatype)
            case pn.Assign(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)]
                    ),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val2)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("2")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.In1()), rn.Reg(rn.Acc()), rn.Im("0")]
                    ),
                ]
            # ----------------------- L_If_Else + L_Loop ----------------------
            case pn.IfElse(pn.Stack(pn.Num(val)), [goto1], [goto2]):
                return (
                    self._single_line_comment(stmt, "#")
                    + [
                        rn.Instr(
                            rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                        ),
                        rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                        rn.Jump(rn.Eq(), goto2),
                    ]
                    + self._single_line_comment(goto1, "#")
                    + self._reti_blocks_stmt(pn.Exp(goto1))
                )
            case pn.Exp(pn.GoTo(pn.Name(val))):
                block_name = val
                return self._single_line_comment(stmt, "#") + [
                    rn.Jump(rn.Always(), rn.Name(block_name))
                ]
            # ----------------------------- L_Fun -----------------------------
            case pn.StackMalloc(val):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(val)])
                ]
            case pn.NewStackframe(pn.Num(arg_count)):
                # TODO(frame-layout): adapt this sequence for
                # [args][return address][previous BAF][locals].
                frame_size = 2 + int(arg_count)
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Move(),
                        [rn.Reg(rn.Baf()), rn.Reg(rn.Acc())],
                    ),
                    rn.Instr(
                        rn.Move(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.Baf())],
                    ),
                    rn.Instr(
                        rn.Subi(),
                        [rn.Reg(rn.Sp()), rn.Im("2")],
                    ),
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("0")],
                    ),
                    rn.Instr(
                        rn.Loadi(),
                        [
                            rn.Reg(rn.Acc()),
                            rn.BinOp(
                                rn.Name("_this_instruction"),
                                rn.Add(),
                                4 + (3 if global_vars.args.no_long_jumps else 0),
                            ),
                        ],
                    ),
                    rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("-1")],
                    ),
                ]
            case pn.RemoveStackframe(pn.Num(local_var_count)):
                # TODO(frame-layout): adapt teardown for
                # [args][return address][previous BAF][locals].
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Baf()), rn.Reg(rn.Baf()), rn.Im("0")]
                    ),
                    # had to implmented this way because of interrupts overwitting the BAF address
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Baf()), rn.Im(str(int(local_var_count) + 2))]),
                    rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.Sp())]),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Baf()), rn.Im(str(int(local_var_count) + 2))]),
                ]
            case pn.Return(pn.Stack(pn.Num(val))):
                # TODO(frame-layout): update return-address access for the new
                # frame layout.
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")]
                    ),
                ]
            case pn.Return(pn.Empty()):
                # TODO(frame-layout): update return-address access for the new
                # frame layout.
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")]
                    ),
                ]
            case _:
                throw_error(stmt)

    def reti_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(_, blocks):
                reti_blocks = []
                for block in blocks:
                    match block:
                        case pn.Block(_, stmts):
                            instrs = []
                            for stmt in stmts:
                                instrs += self._reti_blocks_stmt(stmt)
                            block.stmts_instrs[:] = instrs
                        case _:
                            throw_error(block)
                reti_blocks = blocks
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_blocks"),
                    reti_blocks,
                )
            case _:
                throw_error(file)

    # =========================================================================
    # =                               RETI_Patch                              =
    # =========================================================================
    # - deal with large immediates
    # - deal with goto directly to next block
    # - deal with division by 0
    # - what if the main fun isn't the first fun in the file
    # - what is there's no main function

    def count_instrs(self, instrs):
        cnt = 0
        for instr in instrs:
            match instr:
                case pn.SingleLineComment():
                    pass
                case rn.Jump(rn.Eq(), pn.GoTo()) if global_vars.args.no_long_jumps:
                    cnt += 5
                case rn.Jump(rn.Always(), rn.Name()) if global_vars.args.no_long_jumps:
                    cnt += 4
                case _:
                    cnt += 1
        return cnt

    def _write_large_immediate_in_register(self, reg, s_num):
        bits = Bits(int=s_num, length=32).bin
        h_bits = bits[0:22]
        l_bits = bits[22:32]
        h_num = Bits(bin=h_bits).int
        l_num = Bits(bin="0" + l_bits).int
        return self._single_line_comment(reg, "# write large immediate into") + [
            rn.Instr(rn.Loadi(), [reg, rn.Im(str(h_num))]),
            rn.Instr(rn.Multi(), [reg, rn.Im(str(2**10))]),
            rn.Instr(rn.Ori(), [reg, rn.Im(str(l_num))]),
        ]

    def _reti_patch_instr(self, instr, current_block_name, is_last_instr):
        match instr:
            # case pn.Exp(pn.GoTo(pn.Name(val))):
            case rn.Jump(rn.Always(), rn.Name(val)):
                if not is_last_instr:
                    return [instr]
                goto_block_name = val
                goto_block_idx = self.all_blocks[goto_block_name].block_idx
                current_block_idx = self.all_blocks[current_block_name].block_idx
                if current_block_idx - 1 == goto_block_idx:
                    return self._single_line_comment(instr, "# // not included")
                else:
                    return [instr]
            case rn.Instr(rn.Div(), _):
                return self._single_line_comment(
                    instr, "# check division by zero for"
                ) + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                    rn.Jump(rn.NEq(), rn.Im("3")),
                    # ACC=1 is DivisionByZero error
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
                    rn.Jump(rn.Always(), rn.Im("0")),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")]
                    ),
                    instr,
                ]
            # case rn.Instr(rn.Divi(), [_, rn.Im("0")]) doesn't occur
            case rn.Instr((rn.Loadin() | rn.Storein) as op, [reg1, reg2, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) and s_num > 2**31 - 1:
                    raise errors.TooLargeLiteral()
                elif s_num < -(2**21) and s_num > 2**21 - 1:
                    # TODO: internal error if reg1 + u_num over 2^32-1
                    # the ACC register is never used as first arg of LOADIN in
                    # the compilation process
                    match op:
                        case rn.Loadin():
                            return self._write_large_immediate_in_register(
                                rn.Reg(rn.Acc()), s_num
                            ) + [
                                rn.Instr(rn.Add(), [reg1, rn.Reg(rn.Acc())]),
                                rn.Instr(rn.Loadin(), [reg1, reg2, rn.Im("0")]),
                            ]
                        case rn.Storein():
                            return self._write_large_immediate_in_register(
                                rn.Reg(rn.Acc()), s_num
                            ) + [
                                rn.Instr(rn.Add(), [reg1, rn.Reg(rn.Acc())]),
                                rn.Instr(rn.Storein(), [reg1, reg2, rn.Im("0")]),
                            ]
                        case _:
                            throw_error(op)
                else:
                    return [instr]
            case rn.Instr(rn.Loadi(), [reg, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) or s_num > 2**31:
                    sys.exit(1)
                elif s_num < -(2**21) or s_num > 2**21 - 1:
                    return self._write_large_immediate_in_register(reg, s_num)
                else:
                    return [instr]
            case _:
                return [instr]

    def _reti_patch_block(self, block):
        match block:
            case pn.Block(name, instrs):
                current_block_name = name
                patched_instrs = []
                for instr in instrs:
                    patched_instrs += self._reti_patch_instr(
                        instr,
                        current_block_name,
                        instr == instrs[-1],
                    )
                block.stmts_instrs[:] = patched_instrs
                # this has to be done in this pass, because the reti_blocks
                # pass sometimes needs to access this attribute from a block
                # where it hasn't yet beeen determined
                # TODO: Move this into the patch_instructions pass, because
                # in this pass goto(next_block_name) gets removed
                block.instrs_before = pn.Num(str(self.instrs_cnt))
                num_instrs = self.count_instrs(block.stmts_instrs)
                block.num_instrs = pn.Num(str(num_instrs))
                self.instrs_cnt += num_instrs

    def reti_patch(self, file: pn.File):
        match file:
            case pn.File(pn.Name(val), blocks):
                for block in blocks:
                    self._reti_patch_block(block)
                patched_blocks = blocks
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_patch"),
                    patched_blocks,
                )
            case _:
                throw_error(file)

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
            case rn.Instr((rn.Loadin() | rn.Storein()), [_, _, rn.Name(val)]):
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
                (rn.Loadin() | rn.Storein()), [_, _, rn.BinOp(rn.Name(val), op, num)]
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
                                instrs_block_free += self._reti_instr(instr, idx, block)
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
