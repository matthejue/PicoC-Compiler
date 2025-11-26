from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.symbol_table import SymbolTable
from src.utils.util_funs_dependent import (
    throw_type_error,
)
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
        self.current_fun_local_vars_size = 0
        self.rel_fun_addr = 0
        self.stack_type_hints = {}
        # RETI_Blocks
        self.instrs_cnt = 0

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
            case pn.BinOp(left_exp, bin_op, right_exp):
                return pn.BinOp(
                    self._picoc_shrink_exp(left_exp),
                    bin_op,
                    self._picoc_shrink_exp(right_exp),
                )
            case pn.UnOp(un_op, exp):
                return pn.UnOp(un_op, self._picoc_shrink_exp(exp))
            case pn.SizeOf():
                return exp
            # ---------------------------- L_Logic ----------------------------
            case pn.Atom(left_exp, rel, right_exp):
                return pn.Atom(
                    self._picoc_shrink_exp(left_exp),
                    rel,
                    self._picoc_shrink_exp(right_exp),
                )
            case pn.ToBool(exp):
                return pn.ToBool(self._picoc_shrink_exp(exp))
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Alloc():
                return exp
            # ----------------------------- L_Pntr ----------------------------
            case pn.Deref(ref, exp):
                return pn.Deref(
                    self._picoc_shrink_exp(ref), self._picoc_shrink_exp(exp)
                )
            case pn.Ref(ref):
                return pn.Ref(self._picoc_shrink_exp(ref))
            # ---------------------------- L_Array ----------------------------
            case pn.Subscr(ref, exp):
                ref_shrunk = self._picoc_shrink_exp(ref)
                exp_shrunk = self._picoc_shrink_exp(exp)
                return pn.Deref(ref_shrunk, exp_shrunk)
            case pn.Array(exps):
                return pn.Array([self._picoc_shrink_exp(exp) for exp in exps])
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(ref, name):
                return pn.Attr(self._picoc_shrink_exp(ref), name)
            case pn.Struct(assigns):
                assigns_shrinked = []
                for assign in assigns:
                    match assign:
                        case pn.Assign(lhs, exp):
                            assigns_shrinked += [
                                pn.Assign(
                                    lhs,
                                    self._picoc_shrink_exp(exp),
                                )
                            ]
                        case _:
                            throw_type_error(assign)
                return pn.Struct(assigns_shrinked)
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(name, exps):
                return pn.Call(name, [self._picoc_shrink_exp(exp) for exp in exps])
            case _:
                throw_type_error(exp)

    def _picoc_shrink_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
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
            case _:
                throw_type_error(stmt)

    def picoc_shrink(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                filename = val
                decls_defs_shrinked = []
                for decl_def in decls_defs:
                    match decl_def:
                        case pn.FunDef(datatype, pn.Name() as name, allocs, stmts):
                            stmts_shrinked = []
                            for stmt in stmts:
                                stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
                            decls_defs_shrinked += [
                                pn.FunDef(datatype, name, allocs, stmts_shrinked)
                            ]
                        case pn.StructDecl() | pn.FunDecl() | pn.Exp() | pn.Assign():
                            decls_defs_shrinked += [decl_def]
                        case _:
                            throw_type_error(decl_def)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_shrink"),
                    decls_defs_shrinked,
                )
            case _:
                throw_type_error(file)

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
                throw_type_error(decl_def)

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
                throw_type_error(file)

    # =========================================================================
    # =                               PicoC_ANF                               =
    # =========================================================================
    # - bringt AST in A-Normalform:
    # - Funktionen werden aufgelöst

    def _param_size(self, allocs) -> int:
        size = 0
        for alloc in allocs:
            match alloc:
                case pn.Alloc(_, pn.ArrayDecl()):
                    size += 1
                case pn.Alloc(_, datatype):
                    size += self._datatype_size(datatype)
                case _:
                    throw_type_error(alloc)
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
            case pn.ArrayDecl(nums, datatype2):
                size = self._datatype_size(datatype2)
                for num in nums:
                    match num:
                        case pn.Num(val):
                            size *= int(val)
                        case _:
                            throw_type_error(num)
                return size
            case _:
                throw_type_error(datatype)

    def _anf_ref_nodes(self, ref):
        match ref:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val):
                var_name = val
                symbol, chosen_scope = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                if symbol is None:
                    throw_type_error(var_name)
                match chosen_scope:
                    case "global":
                        return [pn.Ref(pn.Global(pn.Name(var_name)))]
                    case _:
                        return [pn.Ref(pn.Stackframe(pn.Num(symbol["addr"])))]
            # ------------------------ L_Pntr + L_Array -----------------------
            case pn.Deref(ptr_exp, idx_exp):
                ptr_nodes = self._anf_ref_nodes(ptr_exp)
                idx_nodes = self._picoc_anf_exp(idx_exp)
                return (
                    ptr_nodes
                    + idx_nodes
                    + [pn.Ref(pn.Deref(pn.Stack(pn.Num("2")), pn.Stack(pn.Num("1"))))]
                )
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(inner_exp, pn.Name() as name):
                exp_nodes = self._anf_ref_nodes(inner_exp)
                return exp_nodes + [pn.Ref(pn.Attr(pn.Stack(pn.Num("1")), name))]
            case pn.Ref(inner):
                return self._anf_ref_nodes(inner)
            case _:
                throw_type_error(ref)


    def _picoc_anf_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val):
                var_name = val
                symbol, choosen_scope = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
                )
                match symbol:
                    case {
                        "type_qual": pn.Writeable(),
                        "datatype": datatype,
                        "name": _,
                        "addr": addr,
                        "size": _,
                    }:
                        name = pn.Name(var_name)
                        num = pn.Num(addr)
                        match choosen_scope, datatype:
                            case ("global", pn.ArrayDecl()):
                                # TODO: struct st1 st = {.ar_var=ar]
                                return [pn.Ref(pn.Global(name))]
                            case ("global", pn.StructSpec()):
                                if self.argmode_on:
                                    size = self._datatype_size(datatype)
                                    return [
                                        pn.Assign(
                                            pn.Stack(pn.Num(str(size))),
                                            pn.Global(name),
                                        )
                                    ]
                                else:
                                    # TODO: struct st2 st = {.st_var=st1]
                                    return [pn.Exp(pn.Global(name))]
                            case (_, pn.ArrayDecl()):
                                return [pn.Ref(pn.Stackframe(num))]
                            case (_, pn.StructSpec()):
                                if self.argmode_on:
                                    size = self._datatype_size(datatype)
                                    return [
                                        pn.Assign(
                                            pn.Stack(pn.Num(str(size))),
                                            pn.Stackframe(num),
                                        )
                                    ]
                                else:
                                    return [pn.Exp(pn.Stackframe(num))]
                            case ("global", _):
                                return [pn.Exp(pn.Global(name))]
                            case (_, _):
                                return [pn.Exp(pn.Stackframe(num))]
                    case {
                        "type_qual": pn.Const(),
                        "datatype": _,
                        "name": _,
                        "val": num,
                        "size": _,
                    }:
                        return [pn.Exp(num)]
                    case _:
                        throw_type_error(symbol)
            case pn.Num() | pn.Char():
                return [pn.Exp(exp)]
            case pn.Call(pn.Name("print") as name, [exp]):
                exp_anf = self._picoc_anf_exp(exp)
                return exp_anf + [pn.Exp(pn.Call(name, [pn.Stack(pn.Num("1"))]))]
            case pn.Call(pn.Name("input"), []):
                return [pn.Exp(exp)]
            case pn.Call(pn.Name("break"), []):
                return [pn.Exp(exp)]
            case pn.SizeOf(exp_datatype):
                size = 1
                match exp_datatype:
                    case pn.Name(val):
                        symbol, _ = self.symbol_table.resolve(
                            val, scope=self.current_scope
                        )
                        size = self._datatype_size(symbol["datatype"])
                    case pn.BinOp() | pn.Num() | pn.Char() | pn.UnOp() | pn.Ref():
                        pass
                    case _:
                        size = self._datatype_size(exp_datatype)
                return [pn.Exp(pn.SizeOf(size))]
            case pn.Exit(pn.Num(val)):
                return [exp_datatype]
            # ----------------------- L_Arith + L_Logic -----------------------
            case pn.BinOp(left_exp, bin_op, right_exp):
                exps1_anf = self._picoc_anf_exp(left_exp)
                exps2_anf = self._picoc_anf_exp(right_exp)
                return (
                    exps1_anf
                    + exps2_anf
                    + [
                        pn.Exp(
                            pn.BinOp(
                                pn.Stack(pn.Num("2")),
                                bin_op,
                                pn.Stack(pn.Num("1")),
                            )
                        )
                    ]
                )
            case pn.UnOp(un_op, exp):
                exps_anf = self._picoc_anf_exp(exp)
                match exp:
                    case pn.Num(val):
                        if val == "2147483648":
                            return [pn.Exp(pn.Num("-2147483648"))]
                return exps_anf + [pn.Exp(pn.UnOp(un_op, pn.Stack(pn.Num("1"))))]
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
            case pn.Alloc(type_qual, datatype, pn.Name(val1), local_var_or_param):
                var_name = val1
                datatype_copy = copy.deepcopy(datatype)
                match self.current_scope:
                    case "global":
                        size = self._datatype_size(datatype_copy)
                        self.symbol_table.declare(
                            var_name,
                            {
                                "type_qual": type_qual,
                                "datatype": datatype_copy,
                                "name": var_name,
                                "addr": pn.Empty(),
                                "size": size,
                            },
                            scope=self.current_scope,
                        )
                    case _:
                        match datatype_copy:
                            case pn.ArrayDecl(nums, datatype2) if (
                                local_var_or_param == "param"
                            ):
                                if len(nums) > 1:
                                    datatype_copy.nums.pop(0)
                                    datatype = pn.PntrDecl(pn.Num("1"), datatype_copy)
                                else:
                                    datatype = pn.PntrDecl(pn.Num("1"), datatype2)
                        size = self._datatype_size(datatype)
                        self.symbol_table.declare(
                            var_name,
                            {
                                "type_qual": type_qual,
                                "datatype": datatype,
                                "name": var_name,
                                "addr": self.rel_fun_addr + size - 1,
                                "size": size,
                                # (
                                #     1
                                #     if local_var_or_param == "param"
                                #     and isinstance(datatype, pn.PntrDecl)
                                #     else size
                                # ),
                            },
                            scope=self.current_scope,
                        )
                        self.rel_fun_addr += size
                        # (
                        #     1
                        #     if local_var_or_param == "param"
                        #     and isinstance(datatype, pn.PntrDecl)
                        #     else size
                        # )
                        self.current_fun_local_vars_size += (
                            size if local_var_or_param == "local_var" else 0
                        )
                # Alloc isn't needed anymore after being evaluated
                return []
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Deref() | pn.Attr():
                final_exp = pn.Exp(pn.Stack(pn.Num("1")))
                refs_anf = self._anf_ref_nodes(exp)
                return refs_anf + [final_exp]
            # ----------------------------- L_Pntr ----------------------------
            # case pn.Ref(pn.Name(val)):
            #     var_name = val
            #     _, choosen_scope = self.symbol_table.resolve(
            #         var_name, scope=self.current_scope
            #     )
            #     name = pn.Name(var_name)
            #     match choosen_scope:
            #         case "global":
            #             return [pn.Ref(pn.Global(name))]
            #         case _:
            #             return [pn.Ref(pn.Stackframe(name))]
            case pn.Ref((pn.Deref() | pn.Attr() | pn.Name()) as ref):
                return self._anf_ref_nodes(ref)
            # ---------------------------- L_Array ----------------------------
            case pn.Array(exps):
                exps_anf = []
                for exp in exps:
                    exps_anf += self._picoc_anf_exp(exp)
                return exps_anf
            # ---------------------------- L_Struct ---------------------------
            case pn.Struct(assigns):
                exps_anf = []
                for assign in assigns:
                    match assign:
                        case pn.Assign(_, exp):
                            exps_anf += self._picoc_anf_exp(exp)
                        case _:
                            throw_type_error(assign)
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
                        throw_type_error(symbol)

                exps_anf = []
                self.argmode_on = True
                for exp2 in exps:
                    exps_anf += self._picoc_anf_exp(exp2)
                self.argmode_on = False

                block_name = pn.Name(fun_name)
                return (
                    self._single_line_comment(exp, "//", filtr=[])
                    + [pn.StackMalloc(2)]
                    + exps_anf
                    + [
                        pn.NewStackframe(block_name),
                        pn.Exp(pn.GoTo(block_name)),
                        pn.RemoveStackframe(),
                    ]
                    + (
                        [pn.Exp(rn.Reg(rn.Acc()))]
                        if not isinstance(return_type, pn.VoidType)
                        else []
                    )
                )
            case _:
                throw_type_error(exp)

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
                stmt_anf = self._picoc_anf_stmt(pn.Assign(name, array_struct))
                return self._single_line_comment(stmt, "//") + stmt_anf
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(pn.Name(val), exp):
                var_name = val
                exps_anf = self._picoc_anf_exp(exp)
                symbol, choosen_scope = self.symbol_table.resolve(
                    var_name, scope=self.current_scope
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
                        match choosen_scope:
                            case "global":
                                name = pn.Name(var_name)
                                return (
                                    self._single_line_comment(stmt, "//")
                                    + exps_anf
                                    + [
                                        pn.Assign(
                                            pn.Global(name),
                                            pn.Stack(num_size),
                                        )
                                    ]
                                )
                            case _:
                                num = pn.Num(addr)
                                return (
                                    self._single_line_comment(stmt, "//")
                                    + exps_anf
                                    + [
                                        pn.Assign(
                                            pn.Stackframe(num),
                                            pn.Stack(num_size),
                                        )
                                    ]
                                )
                    case _:
                        throw_type_error(symbol)
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1)), num
            ):
                var_name = val1
                self.symbol_table.declare(
                    var_name,
                    {
                        "type_qual": type_qual,
                        "datatype": datatype,
                        "name": var_name,
                        "val": num,
                        "size": pn.Empty(),
                    },
                    scope=self.current_scope,
                )
                # Alloc isn't needed anymore after being evaluated
                return self._single_line_comment(stmt, "//") + []
            case pn.Assign(pn.Alloc(_, _, name) as alloc, exp):
                self._picoc_anf_exp(alloc)
                stmt_anf = self._picoc_anf_stmt(pn.Assign(name, exp))
                return self._single_line_comment(stmt, "//") + stmt_anf
            case pn.Assign(ref, exp):
                # Deref, Subscript, Attribute
                exps_anf = self._picoc_anf_exp(exp)
                refs_anf = self._anf_ref_nodes(ref)
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
            case _:
                throw_type_error(stmt)

    def _picoc_anf_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case pn.FunDef(datatype, pn.Name(val1) as name, allocs, blocks):
                fun_name = val1

                self.current_scope = fun_name
                self.symbol_table.set_parent(fun_name, "global")
                self.rel_fun_addr = 0
                self.current_fun_local_vars_size = 0

                blocks_anf = []
                match blocks[0]:
                    case pn.Block(_, stmts):
                        # attach param or not information to alloc
                        # TODO: irgendwann in der Zukunft wird main Argumente haben
                        if fun_name not in [
                            "main",
                            "global",
                        ]:  # TODO: später ändern sobald main tatsächlich Argumente hat
                            for alloc in allocs:
                                alloc.local_var_or_param = "param"

                        param_size = self._param_size(allocs)

                        if not self.symbol_table.contains(fun_name, scope="global"):
                            self.symbol_table.declare(
                                fun_name,
                                {
                                    "datatype": pn.FunDecl(datatype, name, allocs),
                                    "name": fun_name,
                                    "param_size": param_size,  # important for function calls
                                },
                                scope="global",
                            )

                        blocks[0].stmts_instrs[:0] = [pn.Exp(alloc) for alloc in allocs]

                        stmts_anf = []
                        for stmt in blocks[0].stmts_instrs:
                            stmts_anf += self._picoc_anf_stmt(stmt)
                        blocks[0].stmts_instrs[:] = stmts_anf

                        blocks[0].stmts_instrs[:0] = (
                            (
                                self._single_line_comment(decl_def, "//", filtr=[3])
                                if global_vars.args.double_verbose
                                else []
                            )
                            # Other important part of function call
                            + [pn.StackMalloc(self.current_fun_local_vars_size)]
                        )

                        blocks[0].scope = fun_name
                        blocks_anf += [blocks[0]]
                    case _:
                        throw_type_error(blocks[0])
                for block in blocks[1:]:
                    match block:
                        case pn.Block(_, stmts):
                            stmts_anf = []
                            for stmt in stmts:
                                stmts_anf += self._picoc_anf_stmt(stmt)
                            block.stmts_instrs[:] = stmts_anf
                            block.scope = fun_name
                            blocks_anf += [block]
                        case _:
                            throw_type_error(block)

                # add a return if the last instruction is no return
                match blocks[-1]:
                    case pn.Block(_, stmts):
                        blocks[-1].stmts_instrs += (
                            []
                            if stmts and isinstance(stmts[-1], pn.Return)
                            else [pn.Return()]
                        )
                    case _:
                        throw_type_error(blocks[-1])
                return blocks_anf
            case pn.FunDecl(datatype, pn.Name(val1), allocs):
                fun_name = val1

                param_size = self._param_size(allocs)
                self.symbol_table.declare(
                    fun_name,
                    {"datatype": decl_def, "name": fun_name, "param_size": param_size},
                    scope="global",
                )
                # Function declaration isn't needed anymore after being evaluated
                return []
            case pn.StructDecl(pn.Name(val1), allocs):
                struct_name = val1
                attrs = []
                struct_size = 0
                for alloc in allocs:
                    match alloc:
                        case pn.Alloc(pn.Writeable(), datatype, pn.Name(val2)):
                            attr_name = val2
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
                            throw_type_error(alloc)

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
                # Struct declaration isn't needed anymore after being evaluated
                return []
            case pn.Exp() | pn.Assign():
                self.current_scope = "global"
                self.global_stmts_instrs += self._picoc_anf_stmt(decl_def)
                return []
            case _:
                throw_type_error(decl_def)

    def picoc_anf(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                blocks_anf = []
                for decl_def in decls_defs:
                    blocks_anf += self._picoc_anf_def(decl_def)
                # check if there even exists a main function
                global_block = pn.Block("_global_inits", self.global_stmts_instrs)
                global_block.scope = "global"
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_anf"),
                    [global_block] + blocks_anf,
                )
            case _:
                throw_type_error(file)

    # =========================================================================
    # =                            PicoC_Typing                               =
    # =========================================================================
    # - annotates the PicoC AST with datatype information collected during ANF

    def _resolve_stackframe_datatype(self, addr):
        bucket = self.symbol_table._table.get(self.current_scope, {})
        for sym in bucket.values():
            if isinstance(sym, dict) and sym.get("addr") == addr:
                return copy.deepcopy(sym.get("datatype"))
        return None

    def _pointer_like_datatype(self, datatype):
        """Return pointer-view of datatype for arithmetic (arrays decay one level)."""
        match datatype:
            case pn.ArrayDecl(nums, inner_dt):
                # Arrays decay to a pointer to their first element, i.e. drop only
                # the outermost dimension but keep the remaining shape intact.
                if len(nums) > 1:
                    return pn.PntrDecl(
                        pn.Num("1"),
                        pn.ArrayDecl(copy.deepcopy(nums[1:]), copy.deepcopy(inner_dt)),
                    )
                return pn.PntrDecl(pn.Num("1"), copy.deepcopy(inner_dt))
            case pn.PntrDecl():
                return copy.deepcopy(datatype)
            case _:
                return None

    def _deref_result_datatype(self, pointer_dt):
        match pointer_dt:
            case pn.PntrDecl(pn.Num(val), inner_dt):
                if int(val) > 1:
                    return pn.PntrDecl(pn.Num(str(int(val) - 1)), copy.deepcopy(inner_dt))
                return copy.deepcopy(inner_dt)
            case pn.ArrayDecl(nums, inner_dt):
                if len(nums) > 1:
                    return pn.ArrayDecl(nums[1:], copy.deepcopy(inner_dt))
                return copy.deepcopy(inner_dt)
            case _:
                return None

    def _lvalue_datatype(self, ref_obj):
        match ref_obj:
            # TODO: Problem with linking, if function defined in other file
            case pn.Global(pn.Name(val)):
                symbol, _ = self.symbol_table.resolve(val, scope="global")
                return copy.deepcopy(symbol["datatype"]) if symbol else None
            case pn.Stackframe(pn.Num(val)):
                return self._resolve_stackframe_datatype(int(val))
            case pn.Deref(ptr_exp, idx_exp):
                base_dt = self._annotate_exp(ptr_exp)
                self._annotate_exp(idx_exp)
                pointer_dt = self._pointer_like_datatype(base_dt) or base_dt
                return self._deref_result_datatype(pointer_dt) if pointer_dt else None
            case pn.Attr(exp1, pn.Name(attr_name)):
                base_dt = self._annotate_exp(exp1)
                match base_dt:
                    case pn.StructSpec(pn.Name(struct_name)):
                        symbol, _ = self.symbol_table.resolve(
                            attr_name, scope=struct_name
                        )
                        return copy.deepcopy(symbol["datatype"]) if symbol else None
                return None
            case pn.Name(val):
                symbol, _ = self.symbol_table.resolve(val, scope=self.current_scope)
                return copy.deepcopy(symbol["datatype"]) if symbol else None
            case _:
                return None

    def _annotate_ref(self, ref):
        match ref:
            case pn.Ref(ref_obj):
                lvalue_dt = self._lvalue_datatype(ref_obj)
                ref.datatype = lvalue_dt if lvalue_dt else pn.Empty()
                pointer_hint = None
                if lvalue_dt:
                    pointer_hint = self._pointer_like_datatype(
                        copy.deepcopy(lvalue_dt)
                    ) or pn.PntrDecl(pn.Num("1"), copy.deepcopy(lvalue_dt))
                # remember stack-produced values to annotate following Exp(Stack())
                match ref_obj:
                    case pn.Deref(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))):
                        if pointer_hint:
                            # pointer to element lives below the index on the stack
                            self.stack_type_hints[str(val1)] = pointer_hint
                        # index is always an int
                        self.stack_type_hints[str(val2)] = pn.IntType()
                        if lvalue_dt:
                            # deref result is produced on top of the stack
                            self.stack_type_hints["1"] = copy.deepcopy(lvalue_dt)
                    case pn.Attr(pn.Stack(pn.Num(val1)), _):
                        if lvalue_dt:
                            self.stack_type_hints[str(val1)] = lvalue_dt
                    case _:
                        if pointer_hint:
                            # Ref pushes a pointer onto the stack; keep a hint for
                            # the top couple of slots so follow-up Stack() accesses
                            # can be annotated even after one more push.
                            self.stack_type_hints["1"] = pointer_hint
                            self.stack_type_hints["2"] = pointer_hint
                return lvalue_dt
            case _:
                return None

    def _annotate_exp(self, exp):
        match exp:
            # ---------------------------- L_Assign_Alloc ------------------------
            case pn.Exp(inner_exp):
                dtype = self._annotate_exp(inner_exp)
                exp.datatype = dtype if dtype else pn.Empty()
                return exp.datatype
            # ----------------------------- L_Arith ------------------------------
            case pn.Num():
                return pn.IntType()
            case pn.Char():
                return pn.CharType()
            case pn.Name(val):
                symbol, _ = self.symbol_table.resolve(val, scope=self.current_scope)
                return copy.deepcopy(symbol["datatype"]) if symbol else None
            case pn.BinOp(left_exp, bin_op, right_exp):
                l_dt = self._annotate_exp(left_exp)
                r_dt = self._annotate_exp(right_exp)
                left_ptr = self._pointer_like_datatype(l_dt) if l_dt else None
                right_ptr = self._pointer_like_datatype(r_dt) if r_dt else None
                if isinstance(bin_op, (pn.Add, pn.Sub)) and (left_ptr or right_ptr):
                    return left_ptr or right_ptr
                return pn.IntType()
            case pn.UnOp(un_op, inner_exp):
                _ = self._annotate_exp(inner_exp)
                match un_op:
                    case pn.Cast(datatype):
                        return datatype
                    case _:
                        return pn.IntType()
            case pn.SizeOf():
                return pn.IntType()
            # ----------------------------- L_Logic ------------------------------
            case pn.Atom(left_exp, _, right_exp):
                self._annotate_exp(left_exp)
                self._annotate_exp(right_exp)
                return pn.IntType()
            case pn.ToBool(inner_exp):
                self._annotate_exp(inner_exp)
                return pn.IntType()
            # ------------------------ L_Pntr + L_Array -------------------------
            case pn.Ref():
                lvalue_dt = self._annotate_ref(exp)
                if lvalue_dt:
                    return pn.PntrDecl(pn.Num("1"), copy.deepcopy(lvalue_dt))
                return None
            case pn.Deref(ptr_exp, idx_exp):
                base_dt = self._annotate_exp(ptr_exp)
                self._annotate_exp(idx_exp)
                pointer_dt = self._pointer_like_datatype(base_dt) or base_dt
                return self._deref_result_datatype(pointer_dt) if pointer_dt else None
            case pn.Array(exps):
                # assume homogeneous, use first
                elem_dt = self._annotate_exp(exps[0]) if exps else None
                return pn.ArrayDecl([pn.Num(str(len(exps)))], elem_dt) if elem_dt else None
            # ----------------------------- L_Struct ----------------------------
            case pn.Struct(assigns):
                for assign in assigns:
                    self._picoc_typing_stmt(assign)
                return None
            case pn.Attr(inner_exp, pn.Name(attr_name)):
                base_dt = self._annotate_exp(inner_exp)
                match base_dt:
                    case pn.StructSpec(pn.Name(struct_name)):
                        symbol, _ = self.symbol_table.resolve(
                            attr_name, scope=struct_name
                        )
                        return copy.deepcopy(symbol["datatype"]) if symbol else None
                return None
            # ------------------------------ L_Fun ------------------------------
            # TODO: Problem with linking, if function defined in other file
            case pn.Call(pn.Name(fun_name), exps):
                for inner_exp in exps:
                    self._annotate_exp(inner_exp)
                symbol, _ = self.symbol_table.resolve(fun_name, scope="global")
                match symbol:
                    case {"datatype": pn.FunDecl(ret_dt, _, _)}:
                        return copy.deepcopy(ret_dt)
                return None
            case pn.GoTo():
                return None
            case rn.Reg():
                return None
            case pn.Stack(pn.Num(val)):
                hint = self.stack_type_hints.get(str(val))
                return copy.deepcopy(hint) if hint else None
            case pn.Stackframe(pn.Num(val)):
                return self._resolve_stackframe_datatype(int(val))
            case pn.Global(pn.Name(val)):
                symbol, _ = self.symbol_table.resolve(val, scope="global")
                return copy.deepcopy(symbol["datatype"]) if symbol else None
            case pn.Exit():
                return None
            case pn.Empty():
                return None
            case _:
                throw_type_error(exp)

    def _picoc_typing_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(lhs, exp):
                self._annotate_exp(lhs)
                self._annotate_exp(exp)
            case pn.Ref():
                self._annotate_ref(stmt)
            case pn.Exp(exp):
                self._annotate_exp(stmt)
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                self._annotate_exp(exp)
                for inner_stmt in stmts:
                    self._picoc_typing_stmt(inner_stmt)
            case pn.IfElse(exp, stmts1, stmts2):
                self._annotate_exp(exp)
                for inner_stmt in stmts1:
                    self._picoc_typing_stmt(inner_stmt)
                for inner_stmt in stmts2:
                    self._picoc_typing_stmt(inner_stmt)
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                self._annotate_exp(exp)
                for inner_stmt in stmts:
                    self._picoc_typing_stmt(inner_stmt)
            case pn.DoWhile(exp, stmts):
                self._annotate_exp(exp)
                for inner_stmt in stmts:
                    self._picoc_typing_stmt(inner_stmt)
            # ----------------------------- L_Fun -----------------------------
            case pn.Return(exp):
                self._annotate_exp(exp)
            case pn.StackMalloc() | pn.NewStackframe() | pn.RemoveStackframe():
                pass
            case pn.GoTo() | pn.SingleLineComment():
                pass
            case _:
                throw_type_error(stmt)

    def picoc_typing(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(_, decls_defs_blocks):
                for block in decls_defs_blocks:
                    self.current_scope = getattr(block, "scope", "global")
                    match block:
                        case pn.Block(_, stmts_instrs):
                            self.stack_type_hints = {}
                            for stmt in stmts_instrs:
                                self._picoc_typing_stmt(stmt)
                        case _:
                            throw_type_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_typing"),
                    decls_defs_blocks,
                )
            case _:
                throw_type_error(file)

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
                        throw_type_error(prefix)
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
                        throw_type_error(bin_lop)
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
                                rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(str(ord(val)))]
                            )
                        ]
                    case rn.Reg():
                        return reti_instrs + [
                            rn.Instr(rn.Storein(), [rn.Reg(rn.Sp()), exp, rn.Im("1")]),
                        ]
                    case _:
                        throw_type_error(exp)

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
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Baf()),
                                    rn.Reg(rn.Acc()),
                                    rn.Im(str(-(2 + int(val2)))),
                                ],
                            ),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                            ),
                        ]
                return reti_instrs
            case pn.Exp(
                pn.BinOp(pn.Stack(pn.Num(val1)), bin_aop, pn.Stack(pn.Num(val2)))
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
                        throw_type_error(bin_aop)
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val1)]
                    ),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)]
                    ),
                    rn.Instr(aop, [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("2")]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
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
                        throw_type_error(un_op)
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
            case pn.Exp(pn.Call(pn.Name("break"), [])):
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
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
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
                        throw_type_error(rel)
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
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Baf()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(-(2 + int(val2) - int(val1)))),
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
                                                -(
                                                    2
                                                    + int(val1)
                                                    - int(tmp_max)
                                                    + 1
                                                    + int(val2)
                                                )
                                            )
                                        ),
                                    ],
                                ),
                            ]
                        case _:
                            throw_type_error(mem, tmp)
                    tmp.num.val = int(tmp.num.val) + 1
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im(stack_offset)])
                ]
            # ----------------------------- L_Pntr ----------------------------
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
                        reti_instrs += [
                            rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.In1())]),
                            rn.Instr(
                                rn.Subi(), [rn.Reg(rn.In1()), rn.Im(str(int(val) + 2))]
                            ),
                        ]
                    case _:
                        throw_type_error(exp)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")],
                    )
                ]
            case pn.Ref(
                pn.Deref(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))),
                datatype,
            ):
                reti_instrs = self._single_line_comment(stmt, "#")
                # Scale the index by the full size of the referenced datatype
                # (arrays keep their complete shape here, pointers stay size 1).
                help_const = self._datatype_size(datatype)
                match datatype:
                    case pn.ArrayDecl() | pn.IntType() | pn.CharType() | pn.StructSpec():
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)],
                            ),
                            rn.Instr(
                                rn.Multi(), [rn.Reg(rn.In2()), rn.Im(str(help_const))]
                            ),
                            rn.Instr(rn.Add(), [rn.Reg(rn.In1()), rn.Reg(rn.In2())]),
                        ]
                    case pn.PntrDecl(_, datatype2):
                        # for ArrayDecl only 'if local_var_or_parameter.val == "parameter"' keep left
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val1)],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.In2()), rn.Reg(rn.In1()), rn.Im("0")],
                            ),
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Sp()), rn.Reg(rn.In2()), rn.Im(val2)],
                            ),
                            rn.Instr(
                                rn.Multi(), [rn.Reg(rn.In2()), rn.Im(str(help_const))]
                            ),
                            rn.Instr(rn.Add(), [rn.Reg(rn.In1()), rn.Reg(rn.In2())]),
                        ]
                    case _:
                        throw_type_error(datatype)
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")]
                    ),
                ]
            case pn.Ref(
                pn.Attr(pn.Stack(pn.Num(val1)), pn.Name(val2)),
                datatype,
            ):
                attr_name = val2
                rel_pos_in_struct = 0
                match datatype:
                    case pn.StructSpec(pn.Name(val3)):
                        struct_name = val3
                        symbol, _ = self.symbol_table.resolve(
                            struct_name, scope=self.current_scope
                        )
                        attr_ids = symbol["attrs"]
                        for attr_id in attr_ids:
                            if attr_id.val == attr_name:
                                break
                            symbol, _ = self.symbol_table.resolve(
                                attr_id.val, scope=struct_name
                            )
                            attr_size = symbol["size"]
                            rel_pos_in_struct += int(attr_size)
                    case _:
                        throw_type_error(datatype)
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)]
                    ),
                    rn.Instr(
                        rn.Addi(), [rn.Reg(rn.In1()), rn.Im(str(rel_pos_in_struct))]
                    ),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")]
                    ),
                ]
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Exp(pn.Stack(pn.Num(val1)), datatype):
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
                        throw_type_error(datatype)
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
            case pn.NewStackframe(pn.Name(val)):
                fun_block_name = val
                symbol, _ = self.symbol_table.resolve(fun_block_name, scope="global")
                param_size = symbol["param_size"]
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.Acc())]),
                    rn.Instr(
                        rn.Addi(),
                        [rn.Reg(rn.Sp()), rn.Im(str(2 + int(param_size)))],
                    ),
                    rn.Instr(rn.Move(), [rn.Reg(rn.Sp()), rn.Reg(rn.Baf())]),
                    rn.Instr(
                        rn.Subi(),
                        [
                            rn.Reg(rn.Sp()),
                            rn.Im(str(2 + int(param_size))),
                        ],
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

            case pn.RemoveStackframe():
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.In1())]),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.In1()), rn.Reg(rn.Baf()), rn.Im("0")]
                    ),
                    rn.Instr(rn.Move(), [rn.Reg(rn.In1()), rn.Reg(rn.Sp())]),
                ]
            case pn.Return(pn.Stack(pn.Num(val))):
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
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")]
                    ),
                ]
            case _:
                throw_type_error(stmt)

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
                            throw_type_error(block)
                reti_blocks = blocks
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_blocks"),
                    reti_blocks,
                )
            case _:
                throw_type_error(file)

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
                            throw_type_error()
                else:
                    return [instr]
            case rn.Instr(rn.Loadi(), [reg, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) or s_num > 2**31:
                    throw_type_error(instr)
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
                throw_type_error(file)

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
                            throw_type_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti"),
                    instrs_block_free,
                )
            case _:
                throw_type_error(file)
