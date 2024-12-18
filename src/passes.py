import picoc_nodes as pn
import reti_nodes as rn
import errors
import symbol_table as st
from util_funs import (
    throw_error,
    remove_extension,
    convert_to_single_line,
    find_first_pos_in_node,
)
from util_classes import Pos
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
        self.marked_funs_for_error = []
        # PicoC_ANF
        self.argmode_on = False
        self.symbol_table = st.SymbolTable()
        self.current_scope = "global!"
        self.rel_global_addr = 0
        self.rel_fun_addr = 0
        self.global_stmts_instrs = []
        # RETI_Blocks
        self.instrs_cnt = 0
        # RETI_Patch
        self.has_div = False

    # =========================================================================
    # =                              PicoC_Shrink                             =
    # =========================================================================
    def _check_return_stmt(self, stmts, datatype):
        if global_vars.args.supress_errors:
            return ()
        if not stmts:
            match datatype:
                case pn.VoidType():
                    return ()
                case _:
                    return (Pos(-1, -1), "irrelevant")
        match (stmts[-1], datatype):
            case (pn.Return(st.Empty()), pn.VoidType()):
                return ()
            case (pn.Return(exp), pn.VoidType()):
                return (find_first_pos_in_node([exp])[1], "return")
            case (pn.IfElse(_, stmts1, stmts2), _):
                last_stmt_pos1 = self._check_return_stmt(stmts1, datatype)
                if last_stmt_pos1:
                    return last_stmt_pos1
                last_stmt_pos2 = self._check_return_stmt(stmts2, datatype)
                if last_stmt_pos2:
                    return last_stmt_pos2
            case ((pn.DoWhile() | pn.While()), _):
                pass
            case (_, pn.VoidType()):
                return ()
            case (pn.Return(st.Empty()), _):
                return (Pos(-1, -1), "irrelevant")
            case (pn.Return(exp), _):
                return ()
            case (_, _):
                found_pos = find_first_pos_in_node([stmts[-1]])
                if not found_pos:
                    return (Pos(-1, -1), "exp")
                return (found_pos[1], "exp")

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
                            throw_error(assign)
                return pn.Struct(assigns_shrinked)
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(name, exps):
                return pn.Call(name, [self._picoc_shrink_exp(exp) for exp in exps])
            case _:
                throw_error(exp)

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
                throw_error(stmt)

    def picoc_shrink(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                filename = val
                decls_defs_shrinked = []
                for decl_def in decls_defs:
                    match decl_def:
                        case pn.FunDef(
                            datatype, pn.Name(val2, pos2) as name, allocs, stmts
                        ):
                            fun_name = val2
                            fun_pos = pos2

                            last_stmt_pos_exp_or_return = self._check_return_stmt(
                                stmts, datatype
                            )
                            if last_stmt_pos_exp_or_return:
                                match (
                                    last_stmt_pos_exp_or_return[0],
                                    last_stmt_pos_exp_or_return[1],
                                ):
                                    case (last_stmt_pos, return_or_exp):
                                        raise errors.WrongReturnType(
                                            fun_name,
                                            fun_pos,
                                            convert_to_single_line(
                                                datatype, no_colors=True
                                            ),
                                            (
                                                "IntType()"
                                                if isinstance(datatype, pn.VoidType)
                                                else "VoidType()"
                                            ),
                                            (
                                                last_stmt_pos
                                                if last_stmt_pos != Pos(-1, -1)
                                                else fun_pos
                                            ),
                                            return_or_exp == "return",
                                        )
                            stmts_shrinked = []
                            for stmt in stmts:
                                stmts_shrinked += [self._picoc_shrink_stmt(stmt)]
                            decls_defs_shrinked += [
                                pn.FunDef(datatype, name, allocs, stmts_shrinked)
                            ]
                        case pn.StructDecl() | pn.FunDecl() | pn.Exp() | pn.Assign():
                            decls_defs_shrinked += [decl_def]
                        case _:
                            throw_error(decl_def)
                return pn.File(
                    pn.Name(remove_extension(filename) + ".picoc_shrink"),
                    decls_defs_shrinked,
                )
            case _:
                throw_error(file)

    # =========================================================================
    # =                              PicoC_Blocks                             =
    # =========================================================================

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
        return [
            pn.SingleLineComment(prefix, convert_to_single_line(node, no_colors=True))
        ]

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
                throw_error(decl_def)

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
                throw_error(file)

    # =========================================================================
    # =                               PicoC_ANF                               =
    # =========================================================================

    def _datatype_size(self, datatype):
        match datatype:
            # ------------------------ L_Arith + L_Pntr -----------------------
            case pn.IntType() | pn.CharType() | pn.PntrDecl():
                return 1
            # ---------------------------- L_Struct ---------------------------
            case pn.StructSpec(pn.Name(val, pos)):
                struct_type_name = val
                struct_type_pos = pos
                try:
                    symbol = self.symbol_table.resolve(struct_type_name)
                except KeyError:
                    raise errors.UnknownIdentifier(struct_type_name, struct_type_pos)
                match symbol:
                    case st.Symbol(_, _, _, _, _, pn.Num(val)):
                        return int(val)
                    case _:
                        throw_error(symbol)
            # ---------------------------- L_Array ----------------------------
            case pn.ArrayDecl(nums, datatype2):
                size = self._datatype_size(datatype2)
                for num in nums:
                    match num:
                        case pn.Num(val):
                            size *= int(val)
                        case _:
                            throw_error(num)
                return size
            case _:
                throw_error(datatype)

    def _param_size(self, allocs):
        size = 0
        for alloc in allocs:
            match alloc:
                case pn.Alloc(_, pn.ArrayDecl(), _, pn.Name("param")):
                    size += 1
                case pn.Alloc(_, datatype):
                    size += self._datatype_size(datatype)
                case _:
                    throw_error(alloc)
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

    def _check_prototypes(self, prototype_def, prototype_decl):
        if global_vars.args.supress_errors:
            return ()
        for def_datatype, decl_datatype in zip(prototype_def, prototype_decl):
            match (def_datatype, decl_datatype):
                case (
                    pn.Alloc(_, pn.VoidType(), pn.Name(val1)),
                    pn.Alloc(_, pn.VoidType(), pn.Name(val2)),
                ) if val1 == val2:
                    pass
                case (
                    pn.Alloc(_, pn.CharType(), pn.Name(val1)),
                    pn.Alloc(_, pn.CharType(), pn.Name(val2)),
                ) if val1 == val2:
                    pass
                case (
                    pn.Alloc(_, pn.IntType(), pn.Name(val1)),
                    pn.Alloc(_, pn.IntType(), pn.Name(val2)),
                ) if val1 == val2:
                    pass
                case (
                    pn.Alloc(_, pn.PntrDecl(num1, datatype1), pn.Name(val1)),
                    pn.Alloc(_, pn.PntrDecl(num2, datatype2), pn.Name(val2)),
                ) if val1 == val2 and num1 == num2:
                    mismatch = self._check_prototypes(
                        [pn.Alloc(pn.Writeable(), datatype1, pn.Name("tmp"))],
                        [pn.Alloc(pn.Writeable(), datatype2, pn.Name("tmp"))],
                    )
                    if mismatch:
                        return (def_datatype, decl_datatype)
                case (
                    pn.Alloc(_, pn.ArrayDecl(nums1, datatype1), pn.Name(val1)),
                    pn.Alloc(_, pn.ArrayDecl(nums2, datatype2), pn.Name(val2)),
                ) if val1 == val2 and nums1 == nums2:
                    mismatch = self._check_prototypes(
                        [pn.Alloc(pn.Writeable(), datatype1, pn.Name("tmp"))],
                        [pn.Alloc(pn.Writeable(), datatype2, pn.Name("tmp"))],
                    )
                    if mismatch:
                        return (def_datatype, decl_datatype)
                case (
                    pn.Alloc(_, pn.StructSpec(pn.Name(val1)), pn.Name(val3)),
                    pn.Alloc(_, pn.StructSpec(pn.Name(val2)), pn.Name(val4)),
                ) if val3 == val4:
                    pass
                case _:
                    return (def_datatype, decl_datatype)
        else:
            return tuple()

    def _check_args_params(self, args, params):
        if global_vars.args.supress_errors:
            return ()
        if len(args) < len(params):
            return ((len(args), len(params)), "<")
        elif len(args) > len(params):
            return ((len(args), len(params)), ">")
        for arg, param in zip(args, params):
            match (arg, param):
                # TODO: what is with void? --> datatype mismatch
                case (
                    (
                        pn.IntType()
                        | pn.CharType()
                        | pn.Num()
                        | pn.Char()
                        | pn.BinOp()
                        | pn.UnOp()
                        | pn.Atom()
                        | pn.Call()
                    ),
                    pn.Alloc(_, (pn.IntType() | pn.CharType()), _),
                ):
                    pass
                case (
                    (pn.Deref(exp, _) | pn.Subscr(exp, _) | pn.Attr(exp, _)),
                    _,
                ):
                    current_exp = arg
                    access_exp_list = []

                    while not isinstance(current_exp, pn.Name):
                        match current_exp:
                            case pn.Deref(exp) | pn.Subscr(exp) | pn.Attr(exp):
                                access_exp_list += [current_exp]
                                current_exp = exp
                            case _:
                                throw_error(current_exp)

                    access_exp_list[:0] = [current_exp]
                    match current_exp:
                        case pn.Name(val1, pos1):
                            var_name = val1
                            var_pos = pos1
                            symbol, _ = self._resolve_name(var_name, var_pos)
                            match symbol:
                                case st.Symbol(_, datatype):
                                    current_dt = copy.deepcopy(datatype)
                                case _:
                                    throw_error(symbol)
                        case _:
                            throw_error(current_exp)

                    current_exp = access_exp_list.pop()
                    while access_exp_list:
                        match (current_exp, current_dt):
                            case (
                                pn.Subscr() | pn.Deref(),
                                pn.ArrayDecl(nums, datatype),
                            ):
                                current_exp = access_exp_list.pop()
                                if len(nums) > 1:
                                    current_dt.nums.pop(0)
                                else:
                                    current_dt = datatype
                            case (
                                pn.Subscr() | pn.Deref(),
                                pn.PntrDecl(num, datatype),
                            ):
                                current_exp = access_exp_list.pop()
                                if int(num.val) > 1:
                                    current_dt.num.val = str(
                                        int(current_dt.num.val) - 1
                                    )
                                else:
                                    current_dt = datatype
                            case (
                                pn.Attr(exp, pn.Name(val2, pos2)),
                                pn.StructSpec(pn.Name(val3, pos3)),
                            ):
                                current_exp = access_exp_list.pop()

                                attr_name = val2
                                attr_pos = pos2
                                struct_type_name = val3
                                struct_type_pos = pos3

                                try:
                                    symbol = self.symbol_table.resolve(
                                        f"{attr_name}@{struct_type_name}"
                                    )
                                except KeyError:
                                    symbol = self.symbol_table.resolve(struct_type_name)
                                    match symbol:
                                        case st.Symbol(_, _, pn.Name(_, pos1)):
                                            struct_type_pos = pos1
                                            raise errors.UnknownAttribute(
                                                attr_name,
                                                attr_pos,
                                                struct_type_name,
                                                struct_type_pos,
                                                var_name,
                                                var_pos,
                                            )

                                # TODO: UnknownAttribute
                                match symbol:
                                    case st.Symbol(_, datatype):
                                        current_dt = datatype
                                    case _:
                                        throw_error(symbol)
                            case _:
                                pass
                    match (current_dt, param):
                        case (
                            (pn.IntType() | pn.CharType()),
                            pn.Alloc(_, (pn.IntType() | pn.CharType()), _),
                        ):
                            pass
                        case (pn.ArrayDecl(), pn.Alloc(_, pn.ArrayDecl(), _)):
                            pass
                        case (
                            (pn.ArrayDecl() | pn.PntrDecl()),
                            pn.Alloc(_, pn.PntrDecl(), _),
                        ):
                            pass
                        case (
                            (pn.StructSpec(name1)),
                            pn.Alloc(_, pn.StructSpec(name2), _),
                        ) if name1 == name2:
                            pass
                        case _:
                            return ((current_dt, arg), param)
                case (
                    pn.Name(val1, pos1),
                    pn.Alloc(_, (pn.IntType() | pn.CharType()), _),
                ):
                    symbol = self._resolve_name(val1, pos1)[0]
                    match symbol:
                        case st.Symbol(_, datatype):
                            match datatype:
                                case pn.CharType() | pn.IntType():
                                    pass
                                case _:
                                    return ((datatype, arg), param)
                        case _:
                            throw_error(symbol)
                case (
                    pn.Ref(exp1),
                    _,
                ):
                    match param:
                        case pn.Alloc(_, pn.PntrDecl(num2, datatype2) as pntrdecl, _):
                            if int(num2.val) > 1:
                                pntrdecl_copy = copy.deepcopy(pntrdecl)
                                pntrdecl_copy.num.val = str(
                                    int(pntrdecl_copy.num.val) - 1
                                )
                                mismatch = self._check_args_params(
                                    [exp1],
                                    [
                                        pn.Alloc(
                                            pn.Writeable(),
                                            pntrdecl_copy,
                                            pn.Name("tmp"),
                                        )
                                    ],
                                )
                            else:
                                mismatch = self._check_args_params(
                                    [exp1],
                                    [
                                        pn.Alloc(
                                            pn.Writeable(),
                                            datatype2,
                                            pn.Name("tmp"),
                                        )
                                    ],
                                )
                            if mismatch:
                                ((datatype_from_mismatch, _), _) = mismatch
                                return (
                                    (
                                        pn.PntrDecl(
                                            pn.Num("1"), datatype_from_mismatch
                                        ),
                                        arg,
                                    ),
                                    param,
                                )
                        case _:
                            match exp1:
                                case (
                                    pn.Num()
                                    | pn.Char()
                                    | pn.BinOp()
                                    | pn.UnOp()
                                    | pn.Atom()
                                    | pn.Deref()
                                ):
                                    determined_datatype = pn.IntType()
                                case pn.Name(val1, pos1):
                                    symbol = self._resolve_name(val1, pos1)[0]
                                    match symbol:
                                        case st.Symbol(_, datatype):
                                            determined_datatype = datatype
                                        case _:
                                            throw_error(symbol)
                                case _:
                                    throw_error(param)
                            return (
                                (pn.PntrDecl(pn.Num("1"), determined_datatype), arg),
                                param,
                            )
                case (
                    (pn.Name() | pn.ArrayDecl() | pn.PntrDecl()),
                    pn.Alloc(_, pn.PntrDecl(num2, datatype2) as pntrdecl, _),
                ):
                    match arg:
                        case pn.Name():
                            symbol = self._resolve_name(arg.val, arg.pos)[0]
                        case _:
                            symbol = st.Symbol(
                                st.Empty(),
                                arg,
                            )
                    match symbol:
                        case st.Symbol(_, datatype1):
                            match datatype1:
                                case pn.PntrDecl(num1, datatype1_2) if num1 == num2:
                                    mismatch = self._check_args_params(
                                        [datatype1_2],
                                        [
                                            pn.Alloc(
                                                pn.Writeable(),
                                                datatype2,
                                                pn.Name("tmp"),
                                            )
                                        ],
                                    )
                                    if mismatch:
                                        return ((datatype1, arg), param)
                                case pn.ArrayDecl(nums1, datatype1_2) as arraydecl:
                                    if len(nums1) > 1 and int(num2.val) == 1:
                                        arraydecl_copy = copy.deepcopy(arraydecl)
                                        arraydecl_copy.nums.pop(0)
                                        mismatch = self._check_args_params(
                                            [arraydecl_copy],
                                            [
                                                pn.Alloc(
                                                    pn.Writeable(),
                                                    datatype2,
                                                    pn.Name("tmp"),
                                                )
                                            ],
                                        )
                                    elif len(nums1) > 1 and int(num2.val) > 1:
                                        arraydecl_copy = copy.deepcopy(arraydecl)
                                        arraydecl_copy.nums.pop(0)
                                        pntrdecl_copy = copy.deepcopy(pntrdecl)
                                        pntrdecl_copy.num.val = str(
                                            int(pntrdecl_copy.num.val) - 1
                                        )
                                        mismatch = self._check_args_params(
                                            [arraydecl_copy],
                                            [
                                                pn.Alloc(
                                                    pn.Writeable(),
                                                    pntrdecl_copy,
                                                    pn.Name("tmp"),
                                                )
                                            ],
                                        )
                                    elif len(nums1) == 1 and int(num2.val) > 1:
                                        pntrdecl_copy = copy.deepcopy(pntrdecl)
                                        pntrdecl_copy.num.val = str(
                                            int(pntrdecl_copy.num.val) - 1
                                        )
                                        mismatch = self._check_args_params(
                                            [datatype1_2],
                                            [
                                                pn.Alloc(
                                                    pn.Writeable(),
                                                    pntrdecl_copy,
                                                    pn.Name("tmp"),
                                                )
                                            ],
                                        )
                                    else:
                                        mismatch = self._check_args_params(
                                            [datatype1_2],
                                            [
                                                pn.Alloc(
                                                    pn.Writeable(),
                                                    datatype2,
                                                    pn.Name("tmp"),
                                                )
                                            ],
                                        )
                                    if mismatch:
                                        return ((datatype1, arg), param)
                                case _:
                                    return ((datatype1, arg), param)
                case (
                    (pn.Name() | pn.ArrayDecl()),
                    pn.Alloc(_, pn.ArrayDecl(nums2, datatype2) as arraydecl, _),
                ):
                    match arg:
                        case pn.Name():
                            symbol = self._resolve_name(arg.val, arg.pos)[0]
                        case _:
                            symbol = st.Symbol(
                                st.Empty(),
                                arg,
                            )
                    match symbol:
                        case st.Symbol(_, datatype1):
                            match datatype1:
                                case pn.ArrayDecl(nums1, datatype1_2) if nums1 == nums2:
                                    mismatch = self._check_args_params(
                                        [datatype1_2],
                                        [
                                            pn.Alloc(
                                                pn.Writeable(),
                                                datatype2,
                                                pn.Name("tmp"),
                                            )
                                        ],
                                    )
                                    if mismatch:
                                        return ((datatype1, arg), param)
                                #  case pn.PntrDecl(num, datatype1_2) as pntrdecl:
                                #      if int(num.val) == 1 and len(nums2) > 1:
                                #          arraydecl_copy = copy.deepcopy(arraydecl)
                                #          arraydecl_copy.nums.pop(0)
                                #          mismatch = self._check_args_params(
                                #              [datatype1_2],
                                #              [
                                #                  pn.Alloc(
                                #                      pn.Writeable(),
                                #                      arraydecl_copy,
                                #                      pn.Name("tmp"),
                                #                  )
                                #              ],
                                #          )
                                #      elif int(num.val) > 1 and len(nums2) > 1:
                                #          pntrdecl_copy = copy.deepcopy(pntrdecl)
                                #          pntrdecl_copy.num.val = str(int(num.val) - 1)
                                #          arraydecl_copy = copy.deepcopy(arraydecl)
                                #          arraydecl_copy.nums.pop(0)
                                #          mismatch = self._check_args_params(
                                #              [pntrdecl_copy],
                                #              [
                                #                  pn.Alloc(
                                #                      pn.Writeable(),
                                #                      arraydecl_copy,
                                #                      pn.Name("tmp"),
                                #                  )
                                #              ],
                                #          )
                                #      elif int(num.val) > 1 and len(nums2) == 1:
                                #          pntrdecl_copy = copy.deepcopy(pntrdecl)
                                #          pntrdecl_copy.num.val = str(int(num.val) - 1)
                                #          mismatch = self._check_args_params(
                                #              [pntrdecl_copy],
                                #              [
                                #                  pn.Alloc(
                                #                      pn.Writeable(),
                                #                      datatype2,
                                #                      pn.Name("tmp"),
                                #                  )
                                #              ],
                                #          )
                                #
                                #      else:
                                #          mismatch = self._check_args_params(
                                #              [datatype1_2],
                                #              [
                                #                  pn.Alloc(
                                #                      pn.Writeable(),
                                #                      datatype2,
                                #                      pn.Name("tmp"),
                                #                  )
                                #              ],
                                #          )
                                #      if mismatch:
                                #          return ((datatype1, arg), param)
                                case _:
                                    return ((datatype1, arg), param)
                        case _:
                            throw_error(symbol)
                case (
                    (pn.StructSpec() | pn.Name()),
                    pn.Alloc(_, pn.StructSpec(name2), _),
                ):
                    match arg:
                        case pn.Name():
                            symbol = self._resolve_name(arg.val, arg.pos)[0]
                        case _:
                            symbol = st.Symbol(
                                st.Empty(),
                                arg,
                            )
                    match symbol:
                        case st.Symbol(_, datatype1):
                            match datatype1:
                                case pn.StructSpec(name1) if name1 == name2:
                                    pass
                                case _:
                                    return ((datatype1, arg), param)
                case _:
                    return ((pn.IntType(), arg), param)
        else:
            return ()

    def _get_leftmost_pos(self, exp):
        while True:
            match exp:
                case pn.Num(_, pos):
                    return st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column)))
                case pn.Name(_, pos):
                    return st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column)))
                case pn.Char(_, pos):
                    return st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column)))
                case pn.BinOp(exp, _, _):
                    return self._get_leftmost_pos(exp)
                case pn.UnOp(_, exp):
                    return self._get_leftmost_pos(exp)
                case pn.Call(name, _):
                    return self._get_leftmost_pos(name)
                case pn.Atom(left_exp, _, _):
                    return self._get_leftmost_pos(left_exp)
                case pn.ToBool(exp):
                    return self._get_leftmost_pos(exp)
                case pn.Ref(ref):
                    return self._get_leftmost_pos(ref)
                case pn.Subscr(ref, _):
                    return self._get_leftmost_pos(ref)
                case pn.Attr(ref, _):
                    return self._get_leftmost_pos(ref)
                case _:
                    throw_error(exp)

    def _add_datatype_and_error_data(self, ref, datatype, error_data: list):
        ref.datatype = datatype
        ref.error_data[0:0] = error_data
        ref.visible += (
            [ref.datatype, ref.error_data] if global_vars.args.double_verbose else []
        )

    def _check_redecl_redef_error(
        self, identifier, identifier_pos, is_fun_or_struct=False
    ):
        at_scope = "" if is_fun_or_struct else f"@{self.current_scope}"
        if self.symbol_table.exists(f"{identifier}{at_scope}"):
            symbol = self.symbol_table.resolve(f"{identifier}{at_scope}")
            match symbol:
                case st.Symbol(
                    _,
                    _,
                    _,
                    _,
                    st.Pos(pn.Num(pos_first_line), pn.Num(pos_first_column)),
                ):
                    raise errors.ReDeclarationOrDefinition(
                        identifier,
                        identifier_pos,
                        Pos(int(pos_first_line), int(pos_first_column)),
                    )
                case _:
                    throw_error(symbol)

    def _resolve_name(self, name, pos):
        try:
            symbol = self.symbol_table.resolve(f"{name}@{self.current_scope}")
            choosen_scope = self.current_scope
        except KeyError:
            try:
                symbol = self.symbol_table.resolve(f"{name}@global!")
                choosen_scope = "global!"
            except KeyError:
                raise errors.UnknownIdentifier(name, pos)
        return symbol, choosen_scope

    def _picoc_anf_ref(self, ref, prev_stmts):
        match ref:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val, pos) as name:
                var_name = val
                var_pos = pos
                # TODO: undefinied identifier error
                symbol, choosen_scope = self._resolve_name(var_name, var_pos)
                match symbol:
                    case st.Symbol(_, datatype, _, _, _, _):
                        current_datatype = copy.deepcopy(datatype)
                    case _:
                        throw_error(symbol)
                while prev_stmts:
                    match current_datatype:
                        case pn.CharType() | pn.IntType():
                            self._add_datatype_and_error_data(
                                prev_stmts.pop(),
                                datatype=current_datatype,
                                error_data=[name],
                            )
                        case pn.PntrDecl(pn.Num(val), datatype):
                            if int(val) == 0:
                                current_datatype = datatype
                                continue
                            self._add_datatype_and_error_data(
                                prev_stmts.pop(),
                                datatype=copy.deepcopy(current_datatype),
                                error_data=[name],
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
                            self._add_datatype_and_error_data(
                                prev_stmts.pop(),
                                datatype=copy.deepcopy(current_datatype),
                                error_data=[name],
                            )
                            current_datatype.nums.pop(0)
                        case pn.StructSpec(pn.Name(val1, _)):
                            struct_type_name = val1
                            #  struct_pos = pos1
                            ref = prev_stmts.pop()
                            self._add_datatype_and_error_data(
                                ref,
                                datatype=current_datatype,
                                error_data=[name],
                            )
                            match ref:
                                case pn.Ref(pn.Attr(_, pn.Name(val2, pos2))):
                                    attr_name = val2
                                    attr_pos = pos2
                                    try:
                                        symbol = self.symbol_table.resolve(
                                            f"{attr_name}@{struct_type_name}"
                                        )
                                    except KeyError:
                                        symbol = self.symbol_table.resolve(
                                            struct_type_name
                                        )
                                        match symbol:
                                            case st.Symbol(_, _, pn.Name(_, pos1)):
                                                struct_type_pos = pos1
                                                raise errors.UnknownAttribute(
                                                    attr_name,
                                                    attr_pos,
                                                    struct_type_name,
                                                    struct_type_pos,
                                                    var_name,
                                                    var_pos,
                                                )
                                case pn.Ref(pn.Subscr()):
                                    raise errors.DatatypeMismatch(
                                        var_name,
                                        "struct",
                                        var_pos,
                                        find_first_pos_in_node([ref])[1],
                                        "array or pointer",
                                    )
                                case pn.Exp():
                                    break
                                case _:
                                    throw_error(ref)
                            match symbol:
                                case st.Symbol(_, datatype):
                                    current_datatype = copy.deepcopy(datatype)
                                case _:
                                    throw_error(symbol)
                        case _:
                            throw_error(current_datatype)

                symbol, choosen_scope = self._resolve_name(var_name, var_pos)
                match symbol:
                    case st.Symbol(_, _, _, val_addr):
                        addr = val_addr
                        match choosen_scope:
                            case "global!":
                                return [pn.Ref(pn.Global(addr))]
                            case _:
                                return [pn.Ref(pn.Stackframe(addr))]
                    case _:
                        throw_error(symbol)
            # ------------------------ L_Pntr + L_Array -----------------------
            case pn.Subscr(ref2, exp):
                ref3 = pn.Ref(pn.Subscr(pn.Stack(pn.Num("2")), pn.Stack(pn.Num("1"))))
                # TODO: this isn't the case anymore
                # for e.g. Deref(ref, Num("0")) for the position
                # Pos(-1, -1) gets saved
                ref3.error_data = (
                    [self._get_leftmost_pos(exp)] if exp.pos != Pos(-1, -1) else []
                )
                # save position
                ref3.pos = find_first_pos_in_node(ref.visible)[1]
                refs_anf = self._picoc_anf_ref(ref2, prev_stmts + [ref3])
                exps_anf = self._picoc_anf_exp(exp)
                return refs_anf + exps_anf + [ref3]
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(ref2, pn.Name(_, pos) as name):
                ref3 = pn.Ref(pn.Attr(pn.Stack(pn.Num("1")), name))
                ref3.error_data = [
                    st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column)))
                ]
                # save position
                ref3.pos = find_first_pos_in_node(ref.visible)[1]
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
                throw_error(ref)

    def _picoc_anf_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val, pos):
                symbol, choosen_scope = self._resolve_name(val, pos)
                match symbol:
                    case st.Symbol(pn.Writeable(), datatype, _, num):
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
                    case st.Symbol(pn.Const(), _, _, num):
                        return [pn.Exp(num)]
                    case _:
                        throw_error(symbol)
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
            case pn.Alloc(type_qual, datatype, pn.Name(val1, pos1), local_var_or_param):
                var_name = val1
                var_pos = pos1
                self._check_redecl_redef_error(var_name, var_pos)
                datatype_copy = copy.deepcopy(datatype)
                match self.current_scope:
                    case "global!":
                        size = self._datatype_size(datatype_copy)
                        symbol = st.Symbol(
                            type_qual,
                            datatype_copy,
                            pn.Name(f"{var_name}@{self.current_scope}"),
                            pn.Num(str(self.rel_global_addr)),
                            st.Pos(
                                pn.Num(str(var_pos.line)), pn.Num(str(var_pos.column))
                            ),
                            pn.Num(str(size)),
                        )
                        self.symbol_table.declare(symbol)
                        self.rel_global_addr += size
                    case _:
                        match datatype_copy:
                            case pn.ArrayDecl(
                                nums, datatype2
                            ) if local_var_or_param.val == "param":
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
                            st.Pos(
                                pn.Num(str(var_pos.line)), pn.Num(str(var_pos.column))
                            ),
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
                final_exp.error_data = []
                refs_anf = self._picoc_anf_ref(exp, [final_exp])
                return refs_anf + [final_exp]
            # ----------------------------- L_Pntr ----------------------------
            case pn.Ref(pn.Name(val, pos)):
                identifier_name = val
                identifier_pos = pos
                symbol, choosen_scope = self._resolve_name(val, pos)
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, num):
                        match choosen_scope:
                            case "global!":
                                return [pn.Ref(pn.Global(num))]
                            case _:
                                return [pn.Ref(pn.Stackframe(num))]
                    case st.Symbol(pn.Const(), datatype):
                        raise errors.DatatypeMismatch(
                            identifier_name,
                            "const " + convert_to_single_line(datatype, no_colors=True),
                            identifier_pos,
                            identifier_pos,
                            #  find_first_pos_in_node([exp])[1],
                            convert_to_single_line(datatype, no_colors=True),
                        )
                    case _:
                        throw_error(symbol)
            case pn.Ref((pn.Subscr() | pn.Attr()) as ref):
                return self._picoc_anf_ref(ref, [])
            # ---------------------------- L_Array ----------------------------
            case pn.Array(exps):
                #  case pn.Array(exps, datatype):
                exps_anf = []
                #  match datatype:
                #      case pn.ArrayDecl(nums, _):
                #          if int(nums[0].val) != len(exps):
                #              raise errors.ArrayInitNotEnoughDims()
                #      case _:
                #          bug_in_compiler(datatype)
                for exp in exps:
                    # add datatype from array to exp
                    # TODO: drüber nachdenken, was ist, wenn
                    # eine Funktion einen Pointer oder Struct
                    # returnt
                    #  dt_array = copy.deepcopy(datatype)
                    #  match (dt_array, exp):
                    #      case (pn.ArrayDecl(_), pn.Array()):
                    #          dt_array.nums.pop(0)
                    #          exp.datatype = dt_array
                    #          exp.visible += (
                    #              [exp.datatype]
                    #              if global_vars.args.double_verbose
                    #              else []
                    #          )
                    #      case (pn.ArrayDecl([pn.Num()], datatype2), pn.Struct()):
                    #          match datatype2:
                    #              case pn.StructSpec():
                    #                  exp.datatype = datatype2
                    #              case _:
                    #                  bug_in_compiler(datatype2)
                    #          exp.visible += (
                    #              [exp.datatype]
                    #              if global_vars.args.double_verbose
                    #              else []
                    #          )
                    #      case (pn.ArrayDecl([pn.Num()], dt_array), _):
                    #          # TODO maybe
                    #          pass
                    #      case _:
                    #          bug_in_compiler(dt_array, exp)
                    # epxressions should be evaluated in reversed order
                    exps_anf += self._picoc_anf_exp(exp)
                return exps_anf
            # ---------------------------- L_Struct ---------------------------
            #  case pn.Struct(assigns, datatype):
            case pn.Struct(assigns):
                exps_anf = []
                #  match datatype:
                #      case pn.StructSpec(pn.Name(val1)):
                #          struct_name = val1
                #      case _:
                #          # TODO
                #          raise errors.DatatypeMismatch()
                #  symbol = self.symbol_table.resolve(f"{struct_name}")
                #  match symbol:
                #      case st.Symbol(_, _, _, val2):
                #          attr_ids = copy.deepcopy(val2)
                #      case _:
                #          bug_in_compiler(symbol)
                for assign in assigns:
                    match assign:
                        case pn.Assign(_, exp):
                            #  case pn.Assign(pn.Name(val3), exp):
                            #  attr_name = val3
                            #  # TODO: this part is only for error messages
                            #  # Fehlermeldung, wenn dieses Attribut garnicht existiert
                            #  # raise errors.UnknownAttributeError
                            #  attr_ids.remove(pn.Name(f"{attr_name}@{struct_name}"))
                            #  symbol = self.symbol_table.resolve(
                            #      f"{attr_name}@{struct_name}"
                            #  )
                            #  match symbol:
                            #      case st.Symbol(_, datatype2):
                            #          dt_attr = copy.deepcopy(datatype2)
                            #          match (dt_attr, exp):
                            #              case (pn.StructSpec(), pn.Struct()):
                            #                  exp.datatype = dt_attr
                            #                  exp.visible += (
                            #                      [exp.datatype]
                            #                      if global_vars.args.double_verbose
                            #                      else []
                            #                  )
                            #              case (
                            #                  (pn.ArrayDecl() | pn.PntrDecl()),
                            #                  pn.Array(),
                            #              ):
                            #                  exp.datatype = dt_attr
                            #                  exp.visible += (
                            #                      [exp.datatype]
                            #                      if global_vars.args.double_verbose
                            #                      else []
                            #                  )
                            #              # TODO: spezielle Behandlung bei CharType
                            #              case ((pn.IntType() | pn.CharType()), _):
                            #                  pass
                            #              case _:
                            #                  # TODO:
                            #                  raise errors.DatatypeMismatch(dt_attr, exp)
                            #      case _:
                            #          bug_in_compiler(symbol)
                            exps_anf += self._picoc_anf_exp(exp)
                        case _:
                            throw_error(assign)
                #  if attr_ids:
                #      # TODO: Error implementieren oder alternativ alle diese
                #      # values mit 0 initialisieren
                #      raise errors.StructInitAttrsMissing(attr_ids, exp)
                return exps_anf
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(pn.Name(val, pos) as name, exps):
                fun_name = val
                fun_call_pos = pos
                args = exps

                # return type for decision about Exp(Reg(Acc())) later
                # params for mismatched allocs
                try:
                    symbol = self.symbol_table.resolve(fun_name)
                    match symbol:
                        case st.Symbol(
                            _, pn.FunDecl(datatype, pn.Name(_, pos2), allocs)
                        ):
                            fun_pos = pos2
                            params = allocs
                            return_type = datatype
                        case _:
                            throw_error(symbol)
                except KeyError:
                    raise errors.UnknownIdentifier(fun_name, fun_call_pos)

                #  check if function call args match with function parameters
                mismatch_dt_alloc = self._check_args_params(args, params)
                if mismatch_dt_alloc:
                    match (mismatch_dt_alloc[0], mismatch_dt_alloc[1]):
                        case (
                            (datatype3, exp3),
                            pn.Alloc(_, datatype4, pn.Name(name4, pos4)),
                        ):
                            argument_exp = convert_to_single_line(exp3, no_colors=True)
                            fun_param_name = name4
                            argument_datatype = convert_to_single_line(
                                datatype3, no_colors=True
                            )
                            fun_param_datatype = convert_to_single_line(
                                datatype4, no_colors=True
                            )
                            argument_pos = find_first_pos_in_node([exp3])[1]
                            fun_param_pos = pos4
                            raise errors.ArgumentMismatch(
                                fun_call_pos,
                                argument_exp,
                                argument_datatype,
                                argument_pos,
                                fun_name,
                                fun_pos,
                                fun_param_name,
                                fun_param_datatype,
                                fun_param_pos,
                            )
                        case ((fun_call_num_args, fun_num_params), rel):
                            raise errors.WrongNumberArguments(
                                rel == "<",
                                fun_call_pos,
                                fun_call_num_args,
                                fun_name,
                                fun_pos,
                                fun_num_params,
                            )
                        case _:
                            throw_error(mismatch_dt_alloc[0], mismatch_dt_alloc[1])
                exps_anf = []
                self.argmode_on = True
                for exp2 in exps:
                    exps_anf += self._picoc_anf_exp(exp2)
                self.argmode_on = False

                block_name = pn.Name(
                    self.fun_name_to_block_name[fun_name], fun_call_pos
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
                throw_error(exp)

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
            case pn.Assign(pn.Name(val, pos), exp):
                var_name = val
                var_pos = pos
                exps_anf = self._picoc_anf_exp(exp)
                symbol, choosen_scope = self._resolve_name(var_name, var_pos)
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, val_addr, _, size):
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
                    case st.Symbol(
                        pn.Const(),
                    ):
                        identifier_name = val
                        identifier_pos = pos
                        raise errors.ConstAssign(identifier_name, identifier_pos)
                    case _:
                        throw_error(symbol)
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1, pos1)), num
            ):
                var_name = val1
                var_pos = pos1
                self._check_redecl_redef_error(var_name, var_pos)
                symbol = st.Symbol(
                    type_qual,
                    datatype,
                    pn.Name(f"{var_name}@{self.current_scope}"),
                    num,
                    st.Pos(pn.Num(str(var_pos.line)), pn.Num(str(var_pos.column))),
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
                throw_error(stmt)

    def _picoc_anf_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case pn.FunDef(datatype, pn.Name(val1, pos1) as name, allocs, blocks):
                def_name = val1
                def_pos = pos1

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
                        #  blocks[0].visible += (
                        #      [blocks[0].param_size, blocks[0].local_vars_size]
                        #      if global_vars.args.double_verbose
                        #      else []
                        #  )

                        blocks[0].stmts_instrs[:] = (
                            (
                                self._single_line_comment(decl_def, "//", filtr=[3])
                                if global_vars.args.double_verbose
                                else []
                            )
                            + [pn.Exp(alloc) for alloc in allocs]
                            + stmts
                        )

                        # check if prototoype of definition and declaration match
                        prototype_def = [
                            pn.Alloc(pn.Writeable(), datatype, name)
                        ] + allocs
                        try:
                            symbol = self.symbol_table.resolve(def_name)

                            match symbol:
                                case st.Symbol(
                                    _,
                                    pn.FunDecl(datatype2, _, allocs),
                                    pn.Name(_, pos2) as name2,
                                ):
                                    decl_pos = pos2
                                    if def_name in self.marked_funs_for_error:
                                        if (
                                            self.marked_funs_for_error.count(def_name)
                                            == 2
                                        ):
                                            raise errors.ReDeclarationOrDefinition(
                                                def_name, def_pos, decl_pos
                                            )
                                        symbol.name.pos = def_pos
                                        self.marked_funs_for_error += [def_name]
                                    prototype_decl = [
                                        pn.Alloc(pn.Writeable(), datatype2, name2)
                                    ] + ([] if isinstance(allocs, st.Empty) else allocs)
                                case _:
                                    throw_error(symbol)

                            mismatched_allocs = self._check_prototypes(
                                prototype_def, prototype_decl
                            )
                            if mismatched_allocs:
                                match (mismatched_allocs[0], mismatched_allocs[1]):
                                    case (
                                        pn.Alloc(_, datatype3, pn.Name(name3, pos3)),
                                        pn.Alloc(_, datatype4, pn.Name(name4, pos4)),
                                    ):
                                        def_param_datatype = datatype3
                                        decl_param_datatype = datatype4
                                        def_param_name = name3
                                        decl_param_name = name4
                                        def_param_pos = pos3
                                        decl_param_pos = pos4
                                        raise errors.PrototypeMismatch(
                                            def_name,
                                            def_pos,
                                            def_param_name,
                                            convert_to_single_line(
                                                def_param_datatype, no_colors=True
                                            ),
                                            def_param_pos,
                                            decl_pos,
                                            decl_param_name,
                                            convert_to_single_line(
                                                decl_param_datatype, no_colors=True
                                            ),
                                            decl_param_pos,
                                        )
                                    case _:
                                        throw_error(
                                            mismatched_allocs[0], mismatched_allocs[1]
                                        )
                        except KeyError:
                            symbol = st.Symbol(
                                st.Empty(),
                                pn.FunDecl(datatype, name, allocs),
                                name,
                                st.Empty(),
                                st.Pos(
                                    pn.Num(str(def_pos.line)),
                                    pn.Num(str(def_pos.column)),
                                ),
                                st.Empty(),
                            )
                            self.symbol_table.declare(symbol)

                        stmts_anf = []
                        for stmt in blocks[0].stmts_instrs:
                            stmts_anf += self._picoc_anf_stmt(stmt)
                        blocks[0].stmts_instrs[:] = stmts_anf

                        blocks_anf += [blocks[0]]
                    case _:
                        throw_error(blocks[0])
                for block in blocks[1:]:
                    match block:
                        case pn.Block(_, stmts):
                            stmts_anf = []
                            for stmt in stmts:
                                stmts_anf += self._picoc_anf_stmt(stmt)
                            block.stmts_instrs[:] = stmts_anf
                            blocks_anf += [block]
                        case _:
                            throw_error(block)

                # add a return if the last instruction is no return
                match blocks[-1]:
                    case pn.Block(_, stmts):
                        blocks[-1].stmts_instrs += (
                            []
                            if stmts and isinstance(stmts[-1], pn.Return)
                            else [pn.Return()]
                        )
                    case _:
                        throw_error(blocks[-1])
                return blocks_anf
            case pn.FunDecl(datatype, pn.Name(val, pos) as name, allocs):
                decl_name = val
                decl_pos = pos
                self._check_redecl_redef_error(
                    decl_name, decl_pos, is_fun_or_struct=True
                )
                symbol = st.Symbol(
                    st.Empty(),
                    decl_def,
                    name,
                    st.Empty(),
                    st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column))),
                    st.Empty(),
                )
                self.symbol_table.declare(symbol)
                # Function declaration isn't needed anymore after being evaluated
                return []
            case pn.StructDecl(pn.Name(val1, pos1) as name, allocs):
                struct_name = val1
                struct_pos = pos1
                attrs = []
                struct_size = 0
                for alloc in allocs:
                    match alloc:
                        case pn.Alloc(pn.Writeable(), datatype, pn.Name(val2, pos2)):
                            attr_name = val2
                            attr_pos = pos2
                            attr_size = self._datatype_size(datatype)
                            self.copy_old_scope = self.current_scope
                            self.current_scope = struct_name
                            self._check_redecl_redef_error(
                                f"{attr_name}",
                                attr_pos,
                            )
                            self.current_scope = self.copy_old_scope
                            symbol = st.Symbol(
                                st.Empty(),
                                datatype,
                                pn.Name(f"{attr_name}@{struct_name}"),
                                st.Empty(),
                                st.Pos(
                                    pn.Num(str(attr_pos.line)),
                                    pn.Num(str(attr_pos.column)),
                                ),
                                pn.Num(str(attr_size)),
                            )
                            self.symbol_table.declare(symbol)
                            attrs += [pn.Name(f"{attr_name}@{struct_name}")]
                            struct_size += attr_size
                        case _:
                            throw_error(alloc)

                self._check_redecl_redef_error(
                    struct_name, struct_pos, is_fun_or_struct=True
                )
                symbol = st.Symbol(
                    st.Empty(),
                    decl_def,
                    name,
                    attrs,
                    st.Pos(pn.Num(str(pos1.line)), pn.Num(str(pos1.column))),
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
                throw_error(decl_def)

    def picoc_anf(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                blocks_anf = []
                for decl_def in decls_defs:
                    blocks_anf += self._picoc_anf_def(decl_def)
                # check if there even exists a main function
                try:
                    main_with_id = self.fun_name_to_block_name["main"]
                except KeyError:
                    raise errors.NoMainFunction()
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
                throw_error(file)

    # =========================================================================
    # =                              RETI_Blocks                              =
    # =========================================================================
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
                    case pn.Num(val, pos, is_negative):
                        if int(val) > 2**31 and is_negative.val == "negative":
                            raise errors.TooLargeLiteral(val, pos)
                        elif int(val) > 2**31 - 1 and is_negative.val == "not_negative":
                            raise errors.TooLargeLiteral(val, pos)
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
                        throw_error(bin_aop)
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
                            throw_error(mem, tmp)
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
                        throw_error(exp)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")],
                    )
                ]
            case pn.Ref(
                pn.Subscr(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))),
                datatype,
                error_data,
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
                                    throw_error(num)
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
                        match error_data:
                            case [
                                pn.Name(val1, pos1),
                                st.Pos(pn.Num(line), pn.Num(column)),
                            ]:
                                match datatype:
                                    case pn.StructSpec():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "struct",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "array or pointer",
                                        )
                                    case pn.IntType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "int",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "array or pointer",
                                        )
                                    case pn.CharType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "char",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "array or pointer",
                                        )
                                    case _:
                                        throw_error(datatype)
                            # bei z.B. Deref(ref, Num("0")) wird für die
                            # Position nur Pos(-1, -1) gespeichert
                            case [pn.Name(val1, pos1)]:
                                match datatype:
                                    case pn.StructSpec():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "struct",
                                            pos1,
                                            pos1,
                                            "array or pointer",
                                        )
                                    case pn.IntType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "int",
                                            pos1,
                                            pos1,
                                            "array or pointer",
                                        )
                                    case pn.CharType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "char",
                                            pos1,
                                            pos1,
                                            "array or pointer",
                                        )
                                    case _:
                                        throw_error(datatype)
                            case _:
                                throw_error(error_data)
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")]
                    ),
                ]
            case pn.Ref(
                pn.Attr(pn.Stack(pn.Num(val1)), pn.Name(val2, pos2)),
                datatype,
                error_data,
            ):
                attr_name = val2
                rel_pos_in_struct = 0
                match datatype:
                    case pn.StructSpec(pn.Name(val3)):
                        # determine relative pos in struct
                        struct_name = val3
                        symbol = self.symbol_table.resolve(struct_name)
                        # TODO: try error and error message
                        match symbol:
                            case st.Symbol(_, _, _, val4):
                                attr_ids = val4
                                for attr_id in attr_ids:
                                    if attr_id.val == f"{attr_name}@{struct_name}":
                                        break
                                    symbol = self.symbol_table.resolve(attr_id.val)
                                    match symbol:
                                        case st.Symbol(_, _, _, _, _, pn.Num(val4)):
                                            attr_size = val4
                                            rel_pos_in_struct += int(attr_size)
                                        case _:
                                            throw_error(symbol)
                            case _:
                                throw_error(symbol)
                    case _:
                        match error_data:
                            case [
                                pn.Name(val1, pos1),
                                st.Pos(pn.Num(line), pn.Num(column)),
                            ]:
                                match datatype:
                                    case pn.ArrayDecl():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "array",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "struct",
                                        )
                                    case pn.PntrDecl():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "pointer",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "struct",
                                        )
                                    case pn.IntType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "int",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "struct",
                                        )
                                    case pn.CharType():
                                        raise errors.DatatypeMismatch(
                                            val1,
                                            "char",
                                            pos1,
                                            Pos(int(line), int(column)),
                                            "struct",
                                        )
                                    case _:
                                        throw_error(datatype)
                            case _:
                                throw_error(error_data)
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
                    + [pn.Exp(goto1)]
                )
            case pn.Exp(pn.GoTo(pn.Name(val))):
                # self._single_line_comment(stmt, "#")
                return [stmt]
            # ----------------------------- L_Fun -----------------------------
            case pn.StackMalloc(pn.Num(val)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(val)])
                ]
            case pn.NewStackframe(pn.Name(val, pos), pn.GoTo() as goto):
                fun_block_name = val
                fun_call_pos = pos
                try:
                    fun_block = self.all_blocks[fun_block_name]
                except KeyError:
                    raise errors.UnknownIdentifier(fun_block_name, fun_call_pos)
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
                        throw_error(num1, num2)
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
                throw_error(stmt)

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
                            throw_error(block)
                reti_blocks = blocks
                return pn.File(
                    pn.Name(remove_extension(val) + ".reti_blocks"), reti_blocks
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
        #  if not (
        #      global_vars.args.verbose
        #      and global_vars.args.double_verbose
        #      and global_vars.args.no_long_jumps
        #  ):
        #      return len(instrs)
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

    #  def _write_large_immediate_in_register(self, reg, s_num):
    #      bits = Bits(int=s_num, length=32).bin
    #      sign = bits[0]
    #      h_bits = bits[1:11]
    #      l_bits = bits[11:32]
    #      h_num = Bits(bin="0" + h_bits).int
    #      l_num = Bits(bin="0" + l_bits).int
    #      return (
    #          self._single_line_comment(reg, "# write large immediate into")
    #          + (
    #              [
    #                  rn.Instr(rn.Loadi(), [reg, rn.Im("-1")]),
    #                  rn.Instr(rn.Multi(), [reg, rn.Im(str(2**10))]),
    #              ]
    #              if h_num == 0
    #              else [rn.Instr(rn.Loadi(), [reg, rn.Im(str(-h_num))])]
    #          )
    #          + [
    #              rn.Instr(rn.Multi(), [reg, rn.Im(str(2**21))]),
    #              rn.Instr(rn.Ori(), [reg, rn.Im(str(l_num))]),
    #          ]
    #          if sign == "1"
    #          else [
    #              rn.Instr(rn.Loadi(), [reg, rn.Im(str(h_num))]),
    #              rn.Instr(rn.Multi(), [reg, rn.Im(str(2**20))]),
    #              rn.Instr(rn.Multi(), [reg, rn.Im("2")]),
    #              rn.Instr(rn.Ori(), [reg, rn.Im(str(l_num))]),
    #          ]
    #      )

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
                            throw_error()
                else:
                    return [instr]
            case rn.Instr(rn.Loadi(), [reg, rn.Im(val)]):
                s_num = int(val)
                if s_num < -(2**31) or s_num > 2**31:
                    throw_error(instr)
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
                # goto_main = pn.Exp(pn.GoTo(pn.Name(main_with_id)))
                # self.global_stmts_instrs += self._single_line_comment(
                #     goto_main, "# //"
                # ) + [goto_main]

                for block in blocks:
                    self._reti_patch_block(block)
                patched_blocks = blocks
                return pn.File(
                    pn.Name(remove_extension(val) + ".reti_patch"),
                    patched_blocks,
                )
            case _:
                throw_error(file)

    # =========================================================================
    # =                                  RETI                                 =
    # =========================================================================

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
                            throw_error(block)
                return rn.Program(
                    rn.Name(remove_extension(val) + ".reti"), instrs_block_free
                )
            case _:
                throw_error(file)
