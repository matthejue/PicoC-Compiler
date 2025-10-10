import picoc_nodes as pn
import reti_nodes as rn
import symbol_table as st
from util_funs import (
    throw_type_error,
    remove_extension,
    convert_to_single_line,
)
import global_vars
import copy
from bitstring import Bits
from inspect import isclass


class Passes:
    def __init__(self):
        # PicoC_Blocks
        self.block_id = 0
        self.all_blocks = dict()
        self.fun_name_to_block_name = dict()
        # PicoC_ANF
        self.argmode_on = False
        self.symbol_table = st.SymbolTable()
        self.current_scope = "global!"
        self.rel_global_addr = 0
        self.rel_fun_addr = 0
        self.global_stmts_instrs = []
        # RETI_Blocks
        self.instrs_cnt = 0

    # =========================================================================
    # =                              PicoC_Shrink                             =
    # =========================================================================
    # - Ersetzen von Deref(exp, i) durch Subscr(exp, i)

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
                # shrink: Deref gets replaced by Subscr
                return pn.Subscr(
                    self._picoc_shrink_exp(ref), self._picoc_shrink_exp(exp)
                )
            case pn.Ref(ref):
                return pn.Ref(self._picoc_shrink_exp(ref))
            # ---------------------------- L_Array ----------------------------
            case pn.Subscr(ref, exp):
                return pn.Subscr(
                    self._picoc_shrink_exp(ref), self._picoc_shrink_exp(exp)
                )
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
            # --------------------------- L_Comment ---------------------------
            case pn.RETIComment():
                return stmt
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
            case pn.Return(st.Empty()):
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
                        case pn.FunDef(
                            datatype, pn.Name() as name, allocs, stmts
                        ):
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
                    pn.Name(remove_extension(filename) + ".picoc_shrink"),
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

    def _single_line_comment(self, node, prefix, filtr=[1, 2, 3]):
        if not (global_vars.args.verbose or global_vars.args.double_verbose):
            return []
        if global_vars.args.example:
            for stmt_instr in global_vars.IMPORTANT_STMTS_INSTRS:
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
            visible_emptied_lists = list(
                map(
                    lambda node, i: (
                        [] if isinstance(node, list) and i in filtr else node
                    ),
                    node.visible,
                    range(0, len(node.visible)),
                )
            )
            node.visible = visible_emptied_lists
        return [pn.SingleLineComment(prefix, convert_to_single_line(node))]

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = pn.Block(
            pn.Name(label),
            stmts,
        )
        blocks[label] = new_block
        self.block_id += 1
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

                # check for redefinition
                if not self.fun_name_to_block_name.get(fun_name):
                    self.fun_name_to_block_name[fun_name] = (
                        f"{fun_name}.{self.block_id}"
                    )
                else:
                    if fun_name not in self.marked_funs_for_error:
                        self.marked_funs_for_error += [fun_name]
                self._create_block(fun_name, processed_stmts, blocks)
                self.all_blocks |= blocks
                return [
                    pn.FunDef(
                        datatype,
                        name,
                        allocs,
                        list(
                            sorted(
                                blocks.values(),
                                key=lambda block: -int(
                                    block.name.val[block.name.val.rfind(".") + 1 :]
                                ),
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
                for decl_def in reversed(decls_defs):
                    decls_defs_blocks += self._picoc_blocks_def(decl_def)
                return pn.File(
                    pn.Name(remove_extension(val) + ".picoc_blocks"),
                    list(reversed(decls_defs_blocks)),
                )
            case _:
                throw_type_error(file)

    # =========================================================================
    # =                               PicoC_ANF                               =
    # =========================================================================
    # - bringt AST in A-Normalform:
    # - Funktionen werden aufgelöst

    def _datatype_size(self, datatype):
        match datatype:
            # ------------------------ L_Arith + L_Pntr -----------------------
            case pn.IntType() | pn.CharType() | pn.PntrDecl():
                return 1
            # ---------------------------- L_Struct ---------------------------
            case pn.StructSpec(pn.Name(val)):
                struct_type_name = val
                symbol = self.symbol_table.resolve(struct_type_name)
                match symbol:
                    case st.Symbol(_, _, _, _, pn.Num(val)):
                        return int(val)
                    case _:
                        throw_type_error(symbol)
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

    def _param_size(self, allocs):
        size = 0
        for alloc in allocs:
            match alloc:
                case pn.Alloc(_, pn.ArrayDecl(), _, pn.Name("param")):
                    size += 1
                case pn.Alloc(_, datatype):
                    size += self._datatype_size(datatype)
                case _:
                    throw_type_error(alloc)
        return size

    def _local_vars_size(self, stmts):
        size = 0
        for stmt in stmts:
            match stmt:
                case pn.Assign(pn.Alloc(_, datatype)) | pn.Exp(pn.Alloc(_, datatype)):
                    size += self._datatype_size(datatype)
                case pn.SingleLineComment() | pn.RETIComment():
                    # const init and normal assign get skipped
                    pass
                case _:
                    break
        return size

    def _add_datatype(self, ref, datatype):
        ref.datatype = datatype
        ref.visible += [ref.datatype] if global_vars.args.double_verbose else []

    def _resolve_name(self, name):
        try:
            symbol = self.symbol_table.resolve(f"{name}@{self.current_scope}")
            choosen_scope = self.current_scope
        except KeyError:
            symbol = self.symbol_table.resolve(f"{name}@global!")
            choosen_scope = "global!"
        return symbol, choosen_scope

    def _picoc_anf_ref(self, ref, prev_stmts):
        match ref:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val) as name:
                var_name = val
                # TODO: undefinied identifier error
                symbol, choosen_scope = self._resolve_name(var_name)
                match symbol:
                    case st.Symbol(_, datatype, _, _, _):
                        current_datatype = copy.deepcopy(datatype)
                    case _:
                        throw_type_error(symbol)
                while prev_stmts:
                    match current_datatype:
                        case pn.CharType() | pn.IntType():
                            self._add_datatype(
                                prev_stmts.pop(),
                                datatype=current_datatype,
                            )
                        case pn.PntrDecl(pn.Num(val), datatype):
                            if int(val) == 0:
                                current_datatype = datatype
                                continue
                            self._add_datatype(
                                prev_stmts.pop(),
                                datatype=copy.deepcopy(current_datatype),
                            )
                            current_datatype.num.val = int(val) - 1
                        case pn.ArrayDecl(nums, datatype):
                            if len(nums) == 0:
                                # TODO: man sollte die Information,
                                # dass am Ende nen CharType dranhängt auch
                                # gesondert betrachten und bei Ref(Name) was dranhängen
                                current_datatype = datatype
                                continue
                            # TODO: think bit about if add_dadatype should be
                            # before or after the pop
                            self._add_datatype(
                                prev_stmts.pop(),
                                datatype=copy.deepcopy(current_datatype),
                            )
                            current_datatype.nums.pop(0)
                        case pn.StructSpec(pn.Name(val1)):
                            struct_type_name = val1
                            ref = prev_stmts.pop()
                            self._add_datatype(
                                ref,
                                datatype=current_datatype,
                            )
                            match ref:
                                case pn.Ref(pn.Attr(_, pn.Name(val2))):
                                    attr_name = val2
                                    symbol = self.symbol_table.resolve(
                                        f"{attr_name}@{struct_type_name}"
                                    )
                                case pn.Exp():
                                    break
                                case _:
                                    throw_type_error(ref)
                            match symbol:
                                case st.Symbol(_, datatype, _, _, _):
                                    current_datatype = copy.deepcopy(datatype)
                                case _:
                                    throw_type_error(symbol)
                        case _:
                            throw_type_error(current_datatype)

                symbol, choosen_scope = self._resolve_name(var_name)
                match symbol:
                    case st.Symbol(_, _, _, val_addr, _):
                        addr = val_addr
                        match choosen_scope:
                            case "global!":
                                return [pn.Ref(pn.Global(addr))]
                            case _:
                                return [pn.Ref(pn.Stackframe(addr))]
                    case _:
                        throw_type_error(symbol)
            # ------------------------ L_Pntr + L_Array -----------------------
            case pn.Subscr(ref2, exp):
                ref3 = pn.Ref(pn.Subscr(pn.Stack(pn.Num("2")), pn.Stack(pn.Num("1"))))
                refs_anf = self._picoc_anf_ref(ref2, prev_stmts + [ref3])
                exps_anf = self._picoc_anf_exp(exp)
                return refs_anf + exps_anf + [ref3]
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(ref2, pn.Name() as name):
                ref3 = pn.Ref(pn.Attr(pn.Stack(pn.Num("1")), name))
                refs_anf = self._picoc_anf_ref(ref2, prev_stmts + [ref3])
                return refs_anf + [ref3]
            case pn.Ref(ref2):
                # TODO: Fehlermeldung, und das nur Placeholder
                last_ref = prev_stmts[-1]
                refs_anf = self._picoc_anf_ref(ref2, prev_stmts)
                last_ref.datatype = pn.ArrayDecl([pn.Num("1")], last_ref.datatype)
                if global_vars.args.double_verbose:
                    last_ref.visible[1] = last_ref.datatype
                return refs_anf
            case _:
                throw_type_error(ref)

    def _picoc_anf_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val):
                symbol, choosen_scope = self._resolve_name(val)
                match symbol:
                    case st.Symbol(pn.Writeable(), datatype, _, num, _):
                        match choosen_scope, datatype:
                            case ("global!", pn.ArrayDecl()):
                                # TODO: struct st1 st = {.ar_var=ar]
                                return [pn.Ref(pn.Global(num))]
                            case ("global!", pn.StructSpec()):
                                if self.argmode_on:
                                    size = self._datatype_size(datatype)
                                    return [
                                        pn.Assign(
                                            pn.Stack(pn.Num(str(size))),
                                            pn.Global(num),
                                        )
                                    ]
                                else:
                                    # TODO: struct st2 st = {.st_var=st1]
                                    return [pn.Exp(pn.Global(num))]
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
                            case ("global!", _):
                                return [pn.Exp(pn.Global(num))]
                            case (_, _):
                                return [pn.Exp(pn.Stackframe(num))]
                    case st.Symbol(pn.Const(), _, _, num, _):
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
            case pn.Exit(pn.Num(val)):
                return [exp]
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
                        exp.is_negative = pn.Name("negative")
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
                    case "global!":
                        size = self._datatype_size(datatype_copy)
                        symbol = st.Symbol(
                            type_qual,
                            datatype_copy,
                            pn.Name(f"{var_name}@{self.current_scope}"),
                            pn.Num(str(self.rel_global_addr)),
                            pn.Num(str(size)),
                        )
                        self.symbol_table.declare(symbol)
                        self.rel_global_addr += size
                    case _:
                        match datatype_copy:
                            case pn.ArrayDecl(nums, datatype2) if (
                                local_var_or_param.val == "param"
                            ):
                                if len(nums) > 1:
                                    datatype_copy.nums.pop(0)
                                    datatype = pn.PntrDecl(pn.Num("1"), datatype_copy)
                                else:
                                    datatype = pn.PntrDecl(pn.Num("1"), datatype2)
                            case _:
                                pass
                        size = self._datatype_size(datatype)
                        symbol = st.Symbol(
                            type_qual,
                            datatype,
                            pn.Name(f"{var_name}@{self.current_scope}"),
                            pn.Num(str(self.rel_fun_addr + size - 1)),
                            (
                                pn.Num("1")
                                if local_var_or_param.val == "param"
                                and isinstance(datatype, pn.PntrDecl)
                                else pn.Num(str(size))
                            ),
                        )
                        self.symbol_table.declare(symbol)
                        self.rel_fun_addr += (
                            1
                            if local_var_or_param.val == "param"
                            and isinstance(datatype, pn.PntrDecl)
                            else size
                        )
                # Alloc isn't needed anymore after being evaluated
                return []
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Subscr() | pn.Attr():
                final_exp = pn.Exp(pn.Stack(pn.Num("1")))
                # in case of *&var
                refs_anf = self._picoc_anf_ref(exp, [final_exp])
                return refs_anf + [final_exp]
            # ----------------------------- L_Pntr ----------------------------
            case pn.Ref(pn.Name(val)):
                identifier_name = val
                symbol, choosen_scope = self._resolve_name(identifier_name)
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, num, _):
                        match choosen_scope:
                            case "global!":
                                return [pn.Ref(pn.Global(num))]
                            case _:
                                return [pn.Ref(pn.Stackframe(num))]
                    case _:
                        throw_type_error(symbol)
            case pn.Ref((pn.Subscr() | pn.Attr()) as ref):
                return self._picoc_anf_ref(ref, [])
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

                symbol = self.symbol_table.resolve(fun_name)
                match symbol:
                    case st.Symbol(_, pn.FunDecl(datatype, pn.Name()), _, _, _):
                        return_type = datatype
                    case _:
                        throw_type_error(symbol)

                exps_anf = []
                self.argmode_on = True
                for exp2 in exps:
                    exps_anf += self._picoc_anf_exp(exp2)
                self.argmode_on = False

                block_name = pn.Name(
                    self.fun_name_to_block_name[fun_name] 
                )
                return (
                    self._single_line_comment(exp, "//", filtr=[])
                    + [pn.StackMalloc(pn.Num("2"))]
                    + exps_anf
                    + [
                        pn.NewStackframe(
                            block_name, pn.GoTo(pn.Name("addr@next_instr"))
                        ),
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
            case pn.RETIComment():
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
                symbol, choosen_scope = self._resolve_name(var_name)
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, val_addr, size):
                        addr = val_addr
                        match choosen_scope:
                            case "global!":
                                return (
                                    self._single_line_comment(stmt, "//")
                                    + exps_anf
                                    + [
                                        pn.Assign(
                                            pn.Global(addr),
                                            pn.Stack(size),
                                        )
                                    ]
                                )
                            case _:
                                return (
                                    self._single_line_comment(stmt, "//")
                                    + exps_anf
                                    + [
                                        pn.Assign(
                                            pn.Stackframe(addr),
                                            pn.Stack(size),
                                        )
                                    ]
                                )
                    case _:
                        throw_type_error(symbol)
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1)), num
            ):
                var_name = val1
                symbol = st.Symbol(
                    type_qual,
                    datatype,
                    pn.Name(f"{var_name}@{self.current_scope}"),
                    num,
                    st.Empty(),
                )
                self.symbol_table.declare(symbol)
                # Alloc isn't needed anymore after being evaluated
                return self._single_line_comment(stmt, "//") + []
            case pn.Assign(pn.Alloc(_, _, name) as alloc, exp):
                self._picoc_anf_exp(alloc)
                stmt_anf = self._picoc_anf_stmt(pn.Assign(name, exp))
                return self._single_line_comment(stmt, "//") + stmt_anf
            case pn.Assign(ref, exp):
                # Deref, Subscript, Attribute
                exps_anf = self._picoc_anf_exp(exp)
                refs_anf = self._picoc_anf_ref(ref, [])
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
            case pn.Return(st.Empty()):
                return [stmt]
            case pn.Return(exp):
                exps_anf = self._picoc_anf_exp(exp)
                return (
                    self._single_line_comment(stmt, "//")
                    + exps_anf
                    + [pn.Return(pn.Stack(pn.Num("1")))]
                )
            case pn.StackMalloc():
                return [stmt]
            case pn.NewStackframe():
                return [stmt]
            case pn.RemoveStackframe():
                return [stmt]
            # ---------------------------- L_Block ----------------------------
            case pn.GoTo(pn.Name(val)):
                return [pn.Exp(stmt)]
            case _:
                throw_type_error(stmt)

    def _picoc_anf_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case pn.FunDef(datatype, pn.Name(val1) as name, allocs, blocks):
                def_name = val1

                self.current_scope = def_name
                self.rel_fun_addr = 0

                blocks_anf = []
                match blocks[0]:
                    case pn.Block(_, stmts):
                        # attach param or not information to alloc
                        # TODO: irgendwann in der Zukunft wird main Argumente haben
                        if def_name not in ["main", "global!"]:
                            for alloc in allocs:
                                alloc.local_var_or_param = pn.Name("param")
                                if global_vars.args.double_verbose:
                                    alloc.visible[3] = alloc.local_var_or_param

                        param_size = self._param_size(allocs)
                        local_vars_size = self._local_vars_size(stmts)
                        blocks[0].param_size = pn.Num(str(param_size))
                        blocks[0].local_vars_size = pn.Num(str(local_vars_size))

                        try:
                            symbol = self.symbol_table.resolve(def_name)
                        except KeyError:
                            symbol = st.Symbol(
                                st.Empty(),
                                pn.FunDecl(datatype, name, allocs),
                                name,
                                st.Empty(),
                                st.Empty(),
                            )
                            self.symbol_table.declare(symbol)

                        blocks[0].stmts_instrs[:] = (
                            (
                                self._single_line_comment(decl_def, "//", filtr=[3])
                                if global_vars.args.double_verbose
                                else []
                            )
                            + [pn.Exp(alloc) for alloc in allocs]
                            + stmts
                        )

                        stmts_anf = []
                        for stmt in blocks[0].stmts_instrs:
                            stmts_anf += self._picoc_anf_stmt(stmt)
                        blocks[0].stmts_instrs[:] = stmts_anf

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
            case pn.FunDecl(datatype, pn.Name() as name, allocs):
                symbol = st.Symbol(
                    st.Empty(),
                    decl_def,
                    name,
                    st.Empty(),
                    st.Empty(),
                )
                self.symbol_table.declare(symbol)
                # Function declaration isn't needed anymore after being evaluated
                return []
            case pn.StructDecl(pn.Name(val1) as name, allocs):
                struct_name = val1
                attrs = []
                struct_size = 0
                for alloc in allocs:
                    match alloc:
                        case pn.Alloc(pn.Writeable(), datatype, pn.Name(val2)):
                            attr_name = val2
                            attr_size = self._datatype_size(datatype)
                            self.copy_old_scope = self.current_scope
                            self.current_scope = struct_name
                            self.current_scope = self.copy_old_scope
                            symbol = st.Symbol(
                                st.Empty(),
                                datatype,
                                pn.Name(f"{attr_name}@{struct_name}"),
                                st.Empty(),
                                pn.Num(str(attr_size)),
                            )
                            self.symbol_table.declare(symbol)
                            attrs += [pn.Name(f"{attr_name}@{struct_name}")]
                            struct_size += attr_size
                        case _:
                            throw_type_error(alloc)

                symbol = st.Symbol(
                    st.Empty(),
                    decl_def,
                    name,
                    attrs,
                    pn.Num(str(struct_size)),
                )
                self.symbol_table.declare(symbol)
                # Struct declaration isn't needed anymore after being evaluated
                return []
            case pn.Exp() | pn.Assign():
                self.current_scope = "global!"
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
                main_with_id = self.fun_name_to_block_name["main"]
                var = pn.File(
                    pn.Name(remove_extension(val) + ".picoc_anf"),
                    [
                        pn.Block(
                            pn.Name(f"_start.{self.block_id}"),
                            self.global_stmts_instrs
                            + self._picoc_anf_stmt(pn.Exp(pn.Call(pn.Name("main"), [])))
                            + self._picoc_anf_stmt(pn.Exp(pn.Exit(pn.Num("0")))),
                        )
                    ]
                    + blocks_anf,
                )
                return var
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
            case pn.RETIComment():
                return [stmt]
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
                    case pn.Num(val, _):
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
                    case pn.Global(pn.Num(val2)):
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [rn.Reg(rn.Ds()), rn.Reg(rn.Acc()), rn.Im(val2)],
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
                    # rn.Call(rn.Name("PRINT"), rn.Reg(rn.Acc())),
                ]
            case pn.Exit(pn.Num(val)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)]),
                    rn.Jump(rn.Always(), rn.Im("0")),
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
                tmp = pn.Stack(pn.Num("0"))
                mem = copy.deepcopy(exp)
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(val1)])
                ]
                while True:
                    match (tmp, mem):
                        case (pn.Stack(pn.Num(val)), _) if val == tmp_max:
                            break
                        case (pn.Stack(pn.Num(val1)), pn.Global(pn.Num(val2))):
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Ds()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(str(int(val2) + int(val1))),
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
                tmp = pn.Stack(pn.Num("0"))
                reti_instrs = []
                stack_offset = val2
                reti_instrs = self._single_line_comment(stmt, "#")
                while True:
                    match (mem, tmp):
                        case (_, pn.Stack(pn.Num(val))) if val == tmp_max:
                            break
                        case (pn.Global(pn.Num(val1)), pn.Stack(pn.Num(val2))):
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
                                        rn.Im(
                                            str(
                                                int(val1) + int(tmp_max) - 1 - int(val2)
                                            )
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
                    tmp.num.val = str(int(tmp.num.val) + 1)
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im(stack_offset)])
                ]
            # ----------------------------- L_Pntr ----------------------------
            case pn.Ref((pn.Global() | pn.Stackframe()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                match exp:
                    case pn.Global(pn.Num(val)):
                        reti_instrs += [
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.In1()), rn.Im(val)]),
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
                pn.Subscr(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))),
                datatype,
            ):
                reti_instrs = self._single_line_comment(stmt, "#")
                match datatype:
                    case pn.ArrayDecl(nums, datatype2):
                        help_const = self._datatype_size(datatype2)
                        for num in nums[1:]:
                            match num:
                                case pn.Num(val3):
                                    help_const *= int(val3)
                                case _:
                                    throw_type_error(num)
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
                        help_const = self._datatype_size(datatype2)
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
                        symbol = self.symbol_table.resolve(struct_name)
                        match symbol:
                            case st.Symbol(_, _, _, val4, _):
                                attr_ids = val4
                                for attr_id in attr_ids:
                                    if attr_id.val == f"{attr_name}@{struct_name}":
                                        break
                                    symbol = self.symbol_table.resolve(attr_id.val)
                                    match symbol:
                                        case st.Symbol(_, _, _, _, pn.Num(val4)):
                                            attr_size = val4
                                            rel_pos_in_struct += int(attr_size)
                                        case _:
                                            throw_type_error(symbol)
                            case _:
                                throw_type_error(symbol)
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
                    + [pn.Exp(goto1)]
                )
            case pn.Exp(pn.GoTo(pn.Name(val))):
                return [stmt]
            # ----------------------------- L_Fun -----------------------------
            case pn.StackMalloc(pn.Num(val)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(val)])
                ]
            case pn.NewStackframe(pn.Name(val), pn.GoTo() as goto):
                fun_block_name = val
                fun_block = self.all_blocks[fun_block_name]
                num1 = fun_block.param_size
                num2 = fun_block.local_vars_size
                match (num1, num2):
                    case (pn.Num(val1), pn.Num(val2)):
                        param_size = val1
                        local_vars_size = val2
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
                                    rn.Im(
                                        str(2 + int(param_size) + int(local_vars_size))
                                    ),
                                ],
                            ),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("0")],
                            ),
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), goto]),
                            rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                            rn.Instr(
                                rn.Storein(),
                                [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("-1")],
                            ),
                        ]
                    case _:
                        throw_type_error(num1, num2)
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
            case pn.Return(st.Empty()):
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
            case pn.File(pn.Name(val), blocks):
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
                    pn.Name(remove_extension(val) + ".reti_blocks"), reti_blocks
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
                case pn.Exp(pn.GoTo()) if global_vars.args.no_long_jumps:
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

    def _reti_patch_instr(self, instr, current_block_idx, is_last_instr):
        match instr:
            case pn.Exp(pn.GoTo(pn.Name(val))):
                if not is_last_instr:
                    return [instr]
                goto_block_name = val
                goto_block = self.all_blocks[goto_block_name]
                goto_block_idx = int(
                    goto_block.name.val[goto_block.name.val.rindex(".") + 1 :]
                )
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
            case pn.Block(pn.Name(val), instrs):
                current_block_name = val
                patched_instrs = []
                for instr in instrs:
                    patched_instrs += self._reti_patch_instr(
                        instr,
                        int(current_block_name[current_block_name.rindex(".") + 1 :]),
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
                block.visible += (
                    [block.instrs_before, block.num_instrs]
                    if global_vars.args.double_verbose
                    else []
                )
                self.instrs_cnt += num_instrs

    def reti_patch(self, file: pn.File):
        match file:
            case pn.File(pn.Name(val), blocks):
                for block in blocks:
                    self._reti_patch_block(block)
                patched_blocks = blocks
                return pn.File(
                    pn.Name(remove_extension(val) + ".reti_patch"),
                    patched_blocks,
                )
            case _:
                throw_type_error(file)

    # =========================================================================
    # =                                  RETI                                 =
    # =========================================================================
    # - keine Blöcke mehr, Knoten genauso zusammengefügt, wie sie in entfernten Blöcken angeordnet waren
    # - GoTo(Name(str)) werden duch einen Immediate mit passender Distanz / Adresse oder einen Sprungbefehl mit passender Distanz Jump(Always(), Im(str(distance))) ersetzt.

    def _patch_too_large_jumps(self, rel, distance, instr):
        if global_vars.args.no_long_jumps:
            #  if (
            #  distance < -(2**21) and distance > 2**21 - 1
            #  ) or global_vars.args.no_jump:
            neg_rel = global_vars.NEG_RELS[str(rel)]
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
            case pn.Exp(pn.GoTo(pn.Name(val))):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return self._patch_too_large_jumps(rn.Always(), distance, instr)
            case rn.Jump(rn.Eq() as rel, pn.GoTo(pn.Name(val))):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return self._patch_too_large_jumps(rel, distance, instr)
            case rn.Instr(rn.Loadi(), [reg, pn.GoTo(_)]):
                rel_addr = str(
                    int(current_block.instrs_before.val)
                    + idx
                    + 4
                    + (3 if global_vars.args.no_long_jumps else 0)
                )
                return self._single_line_comment(instr, "#") + [
                    rn.Instr(rn.Loadi(), [reg, rn.Im(rel_addr)])
                ]
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
                                    case pn.Exp(
                                        pn.GoTo()
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
                return rn.Program(
                    rn.Name(remove_extension(val) + ".reti"), instrs_block_free
                )
            case _:
                throw_type_error(file)
