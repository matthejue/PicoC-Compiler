import picoc_nodes as pn
import reti_nodes as rn
import errors
import symbol_table as st
from global_funs import (
    bug_in_compiler,
    remove_extension,
    filter_out_comments,
    convert_to_single_line,
)
from global_classes import Pos
import global_vars
import copy


class Passes:
    def __init__(self):
        # PicoC_Blocks
        self.block_id = 0
        self.all_blocks = dict()
        self.funs = dict()
        # RETI_Blocks
        self.instrs_cnt = 0
        self.current_scope = "global"
        self.rel_global_addr = 0
        self.rel_fun_addr = 0
        self.symbol_table = st.SymbolTable()

    # =========================================================================
    # =                              PicoC_Shrink                             =
    # =========================================================================
    # =========================================================================
    # =                              PicoC_Blocks                             =
    # =========================================================================

    def _single_line_comment_picoc(self, stmt):
        if not (global_vars.args.verbose or global_vars.args.double_verbose):
            return []
        visible_emptied_lists = list(
            map(lambda node: [] if isinstance(node, list) else node, stmt.visible)
        )
        stmt.visible = visible_emptied_lists
        tmp = global_vars.args.double_verbose
        global_vars.args.double_verbose = True
        comment = [pn.SingleLineComment("//", convert_to_single_line(stmt))]
        global_vars.args.double_verbose = tmp
        return comment

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = pn.Block(
            pn.Name(label),
            self._single_line_comment_picoc(pn.Block(pn.Name(label), [])) + stmts,
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

                return self._single_line_comment_picoc(stmt) + [
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

                return self._single_line_comment_picoc(stmt) + [
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

                return self._single_line_comment_picoc(stmt) + [goto_condition_check]
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

                return self._single_line_comment_picoc(stmt) + [goto_branch]
            # ----------------------------- L_Fun -----------------------------
            case pn.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_blocks_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case pn.FunDef(datatype, pn.Name(fun_name) as name, allocs, stmts):
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_blocks_stmt(
                        stmt, processed_stmts, blocks
                    )
                self.funs[fun_name] = f"{fun_name}.{self.block_id}"
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
            case (pn.FunDecl() | pn.StructDecl()):
                return [decl_def]
            case _:
                bug_in_compiler(decl_def)

    def picoc_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += self._picoc_blocks_def(decl_def)
                return pn.File(
                    pn.Name(remove_extension(val) + ".picoc_blocks"), decls_defs_blocks
                )
            case _:
                bug_in_compiler(file)

    # =========================================================================
    # =                               PicoC_Mon                               =
    # =========================================================================
    def _datatype_size(self, datatype):
        match datatype:
            # ------------------------ L_Arith + L_Pntr -----------------------
            case (pn.IntType() | pn.CharType() | pn.PntrDecl()):
                return 1
            # ---------------------------- L_Struct ---------------------------
            case pn.StructSpec(pn.Name(val)):
                symbol = self.symbol_table.resolve(val)
                match symbol:
                    case st.Symbol(_, _, _, _, _, pn.Num(val)):
                        return int(val)
                    case _:
                        bug_in_compiler(symbol)
            # ---------------------------- L_Array ----------------------------
            case pn.ArrayDecl(nums, datatype2):
                size = self._datatype_size(datatype2)
                for num in nums:
                    match num:
                        case pn.Num(val):
                            size *= int(val)
                        case _:
                            bug_in_compiler(num)
                return size
            case _:
                bug_in_compiler(datatype)

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
                case pn.Ref(ref_loc):
                    return self._get_leftmost_pos(ref_loc)
                case (pn.Subscr(deref_loc, _) | pn.Deref(deref_loc, _)):
                    return self._get_leftmost_pos(deref_loc)
                case pn.Attr(ref_loc, _):
                    return self._get_leftmost_pos(ref_loc)
                case _:
                    bug_in_compiler(exp)

    def _add_datatype_and_error_data(self, ref, datatype, error_data):
        ref.datatype = datatype
        ref.error_data[0:0] = error_data
        ref.visible += ([ref.datatype] if global_vars.args.double_verbose else []) + (
            [ref.error_data] if global_vars.args.double_verbose else []
        )

    def _picoc_mon_ref(self, ref_loc, prev_refs):
        match ref_loc:
            # ---------------------------- L_Arith ----------------------------
            case pn.Name(val) as name:
                var_name = val
                symbol = self.symbol_table.resolve(f"{var_name}@{self.current_scope}")
                match symbol:
                    case st.Symbol(_, datatype):
                        current_datatype = datatype
                    case _:
                        bug_in_compiler(symbol)
                while prev_refs:
                    match current_datatype:
                        case (pn.CharType() | pn.IntType()):
                            self._add_datatype_and_error_data(
                                prev_refs.pop(),
                                datatype=current_datatype,
                                error_data=[name],
                            )
                            break
                        case pn.PntrDecl(pn.Num(val), datatype):
                            self._add_datatype_and_error_data(
                                prev_refs.pop(),
                                datatype=copy.deepcopy(current_datatype),
                                error_data=[name],
                            )
                            if int(val) == 0:
                                current_datatype = datatype
                            current_datatype.num.val = int(val) - 1
                        case pn.ArrayDecl(nums, datatype):
                            self._add_datatype_and_error_data(
                                prev_refs.pop(),
                                datatype=copy.deepcopy(current_datatype),
                                error_data=[name],
                            )
                            if len(nums) == 0:
                                current_datatype = datatype
                            current_datatype.nums = nums[1:]
                        case pn.StructSpec(pn.Name(val1)):
                            struct_name = val1
                            ref = prev_refs.pop()
                            self._add_datatype_and_error_data(
                                ref,
                                datatype=current_datatype,
                                error_data=[name],
                            )
                            match ref:
                                case pn.Ref(pn.Attr(ref_loc, pn.Name(val2))):
                                    attr_name = val2
                                    symbol = self.symbol_table.resolve(
                                        f"{attr_name}@{struct_name}"
                                    )
                                case _:
                                    # TODO: here belongs a proper error message
                                    # nachsehen, ob [] auf Structvariable anwendbar ist
                                    bug_in_compiler(ref)
                            match symbol:
                                case st.Symbol(_, datatype):
                                    current_datatype = datatype
                                case _:
                                    bug_in_compiler(symbol)
                        case _:
                            bug_in_compiler(current_datatype)
                return [pn.Exp(pn.Ref(ref_loc))]
            # ------------------------ L_Pntr + L_Array -----------------------
            # TODO: remove after implementing shrink pass
            case (pn.Deref(deref_loc, exp) | pn.Subscr(deref_loc, exp)):
                #  __import__("pudb").set_trace()
                ref = pn.Ref(pn.Subscr(pn.Stack(pn.Num("2")), pn.Stack(pn.Num("1"))))
                # for e.g. Deref(deref_loc, Num("0")) for the position
                # Pos(-1, -1) gets saved
                ref.error_data = (
                    [self._get_leftmost_pos(exp)] if exp.pos != Pos(-1, -1) else []
                )
                refs_mon = self._picoc_mon_ref(deref_loc, [ref] + prev_refs)
                exps_mon = self._picoc_mon_exp(exp)
                return refs_mon + exps_mon + [pn.Exp(ref)]
            # ---------------------------- L_Struct ---------------------------
            case pn.Attr(ref_loc2, pn.Name(_, pos) as name):
                ref = pn.Ref(pn.Attr(pn.Stack(pn.Num("1")), name))
                ref.error_data = [
                    st.Pos(pn.Num(str(pos.line)), pn.Num(str(pos.column)))
                ]
                refs_mon = self._picoc_mon_ref(ref_loc2, [ref] + prev_refs)
                return refs_mon + [pn.Exp(ref)]
            case _:
                bug_in_compiler(ref_loc)

    def _picoc_mon_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case (pn.Name() | pn.Num() | pn.Char()):
                return [pn.Exp(exp)]
            # ----------------------- L_Arith + L_Logic -----------------------
            case pn.BinOp(left_exp, bin_op, right_exp):
                exps1_mon = self._picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        pn.Exp(
                            pn.BinOp(
                                pn.Stack(pn.Num("2")), bin_op, pn.Stack(pn.Num("1"))
                            )
                        )
                    ]
                )
            case pn.UnOp(un_op, exp):
                exps_mon = self._picoc_mon_exp(exp)
                return exps_mon + [pn.Exp(pn.UnOp(un_op, pn.Stack(pn.Num("1"))))]
            # ---------------------------- L_Logic ----------------------------
            case pn.Atom(left_exp, rel, right_exp):
                exps1_mon = self._picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        pn.Exp(
                            pn.Atom(pn.Stack(pn.Num("2")), rel, pn.Stack(pn.Num("1")))
                        )
                    ]
                )
            case pn.ToBool(exp):
                exps_mon = self._picoc_mon_exp(exp)
                return exps_mon + [pn.Exp(pn.ToBool(pn.Stack(pn.Num("1"))))]
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Alloc(type_qual, datatype, pn.Name(val1, pos1)):
                var_name = val1
                size = self._datatype_size(datatype)
                match self.current_scope:
                    case "main":
                        if self.symbol_table.exists(f"{var_name}@{self.current_scope}"):
                            symbol = self.symbol_table.resolve(
                                f"{var_name}@{self.current_scope}"
                            )
                            match symbol:
                                case st.Symbol(
                                    _,
                                    _,
                                    pn.Name(_),
                                    _,
                                    st.Pos(
                                        pn.Num(pos_first_line), pn.Num(pos_first_column)
                                    ),
                                ):
                                    raise errors.Redefinition(
                                        val1,
                                        pos1,
                                        Pos(int(pos_first_line), int(pos_first_column)),
                                    )
                                case _:
                                    bug_in_compiler(symbol)
                        symbol = st.Symbol(
                            type_qual,
                            datatype,
                            pn.Name(f"{var_name}@{self.current_scope}"),
                            pn.Num(str(self.rel_global_addr)),
                            st.Pos(pn.Num(str(pos1.line)), pn.Num(str(pos1.column))),
                            pn.Num(str(size)),
                        )
                        self.symbol_table.define(symbol)
                        self.rel_global_addr += size
                    case _:
                        if self.symbol_table.exists(f"{var_name}@{self.current_scope}"):
                            symbol = self.symbol_table.resolve(
                                f"{var_name}@{self.current_scope}"
                            )
                            match symbol:
                                case st.Symbol(
                                    _,
                                    _,
                                    pn.Name(),
                                    _,
                                    st.Pos(
                                        pn.Num(pos_first_line), pn.Num(pos_first_column)
                                    ),
                                ):
                                    raise errors.Redefinition(
                                        val1,
                                        pos1,
                                        Pos(int(pos_first_line), int(pos_first_column)),
                                    )
                                case _:
                                    bug_in_compiler(symbol)
                        symbol = st.Symbol(
                            type_qual,
                            datatype,
                            pn.Name(f"{var_name}@{self.current_scope}"),
                            pn.Num(str(self.rel_fun_addr)),
                            st.Pos(pn.Num(str(pos1.line)), pn.Num(str(pos1.column))),
                            pn.Num(str(size)),
                        )
                        self.symbol_table.define(symbol)
                        self.rel_fun_addr += size
                # Alloc isn't needed anymore after being evaluated
                return []
            # ----------------------------- L_Pntr ----------------------------
            case pn.Ref(pn.Name()):
                return [pn.Exp(exp)]
            # TODO: remove Deref after Shrink Pass is implemented
            case pn.Ref((pn.Subscr() | pn.Attr() | pn.Deref()) as ref_loc):
                return self._picoc_mon_ref(ref_loc, [])
            # ---------------------------- L_Array ----------------------------
            case pn.Array(exps, datatype):
                exps_mon = []
                match datatype:
                    case pn.ArrayDecl(nums, _):
                        if int(nums[0].val) != len(exps):
                            raise errors.ArrayInitNotEnoughDims()
                    case _:
                        bug_in_compiler(datatype)
                for exp in exps:
                    # add datatype from array to exp
                    # TODO: drüber nachdenken, was ist, wenn
                    # eine Funktion einen Pointer oder Struct
                    # returnt
                    dt_array = copy.deepcopy(datatype)
                    match (dt_array, exp):
                        case (pn.ArrayDecl(_), pn.Array()):
                            dt_array.nums.pop(0)
                            exp.datatype = dt_array
                            exp.visible += (
                                [exp.datatype]
                                if global_vars.args.double_verbose
                                else []
                            )
                        case (pn.ArrayDecl([pn.Num()], datatype2), pn.Struct()):
                            match datatype2:
                                case pn.StructSpec():
                                    exp.datatype = datatype2
                                case _:
                                    bug_in_compiler(datatype2)
                            exp.visible += (
                                [exp.datatype]
                                if global_vars.args.double_verbose
                                else []
                            )
                        case (pn.ArrayDecl([pn.Num()], dt_array), _):
                            pass
                    exps_mon += self._picoc_mon_exp(exp)
                return exps_mon
            # ---------------------------- L_Struct ---------------------------
            case pn.Struct(assigns, datatype):
                exps_mon = []
                match datatype:
                    case pn.StructSpec(pn.Name(val1)):
                        struct_name = val1
                    case _:
                        bug_in_compiler(datatype)
                symbol = self.symbol_table.resolve(f"{struct_name}")
                match symbol:
                    case st.Symbol(_, _, _, val2):
                        attr_ids = copy.deepcopy(val2)
                    case _:
                        bug_in_compiler(symbol)
                for assign in assigns:
                    match assign:
                        case pn.Assign(pn.Name(val3), exp):
                            attr_name = val3
                            attr_ids.remove(pn.Name(f"{attr_name}@{struct_name}"))
                            symbol = self.symbol_table.resolve(
                                f"{attr_name}@{struct_name}"
                            )
                            match symbol:
                                case st.Symbol(_, datatype2):
                                    dt_attr = copy.deepcopy(datatype2)
                                    match (dt_attr, exp):
                                        case (pn.StructSpec(), pn.Struct()):
                                            exp.datatype = dt_attr
                                            exp.visible += (
                                                [exp.datatype]
                                                if global_vars.args.double_verbose
                                                else []
                                            )
                                        case (pn.ArrayDecl(), pn.Array()):
                                            exp.datatype = dt_attr
                                            exp.visible += (
                                                [exp.datatype]
                                                if global_vars.args.double_verbose
                                                else []
                                            )
                                        case ((pn.IntType() | pn.CharType()), _):
                                            pass
                                        case _:
                                            # TODO:
                                            raise errors.DatatypeMismatch(dt_attr, exp)
                                case _:
                                    bug_in_compiler(symbol)
                            exps_mon += self._picoc_mon_exp(exp)
                        case _:
                            bug_in_compiler(assign)
                if attr_ids:
                    # TODO: Error implementieren oder alternativ alle diese
                    # values mit 0 initialisieren
                    raise errors.StructInitAttrsMissing(attr_ids, exp)
                return exps_mon
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            # TODO: remove after Shrink Pass is implemented
            case (pn.Subscr() | pn.Attr() | pn.Deref()):
                refs_mon = self._picoc_mon_ref(exp, [])
                return refs_mon + [
                    pn.Exp(pn.Subscr(pn.Stack(pn.Num("1")), pn.Num("0")))
                ]
            # ----------------------------- L_Fun -----------------------------
            case pn.Call(name, exps):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon += self._picoc_mon_exp(exp)
                    stack_locs[0:0] = [pn.Stack(pn.Num(str(i + 1)))]
                return exps_mon + [pn.Exp(pn.Call(name, stack_locs))]
            case _:
                bug_in_compiler(exp)

    def _picoc_mon_stmt(self, stmt):
        match stmt:
            # ---------------------------- L_Array ----------------------------
            case pn.Assign(
                pn.Alloc(_, datatype, pn.Name(val) as name) as alloc,
                pn.Array(_) as array,
            ):
                array.datatype = datatype
                array.visible += (
                    [array.datatype] if global_vars.args.double_verbose else []
                )
                exps_mon = self._picoc_mon_exp(array)
                self._picoc_mon_exp(alloc)
                symbol = self.symbol_table.resolve(f"{val}@{self.current_scope}")
                match symbol:
                    case st.Symbol(_, _, _, pn.Num(val1), _, pn.Num(val2)):
                        return (
                            self._single_line_comment_picoc(stmt)
                            + exps_mon
                            + [
                                pn.Assign(
                                    pn.Memory(pn.Num(val1)), pn.Stack(pn.Num(val2))
                                )
                            ]
                        )
                    case _:
                        bug_in_compiler(symbol)
            # ---------------------------- L_Struct ---------------------------
            case pn.Assign(
                pn.Alloc(_, datatype, name) as alloc, pn.Struct(_) as struct
            ):
                struct.datatype = datatype
                struct.visible += (
                    [struct.datatype] if global_vars.args.double_verbose else []
                )
                exps_mon = self._picoc_mon_exp(struct)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [pn.Assign(name, pn.Stack(pn.Num("1")))]
                )
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(pn.Name() as name, exp):
                exps_mon = self._picoc_mon_exp(exp)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [pn.Assign(name, pn.Stack(pn.Num("1")))]
                )
            case pn.Assign(
                pn.Alloc(pn.Const() as type_qual, datatype, pn.Name(val1, pos1)), num
            ):
                var_name = val1
                if self.symbol_table.exists(f"{var_name}@{self.current_scope}"):
                    symbol = self.symbol_table.resolve(
                        f"{var_name}@{self.current_scope}"
                    )
                    match symbol:
                        case st.Symbol(
                            _,
                            _,
                            pn.Name(_),
                            _,
                            st.Pos(pn.Num(pos_first_line), pn.Num(pos_first_column)),
                        ):
                            raise errors.Redeclaration(
                                val1,
                                pos1,
                                Pos(int(pos_first_line), int(pos_first_column)),
                            )
                        case _:
                            bug_in_compiler(symbol)
                symbol = st.Symbol(
                    type_qual,
                    datatype,
                    pn.Name(f"{var_name}@{self.current_scope}"),
                    num,
                    st.Pos(pn.Num(str(pos1.line)), pn.Num(str(pos1.column))),
                    st.Empty(),
                )
                self.symbol_table.define(symbol)
                # Alloc isn't needed anymore after being evaluated
                return self._single_line_comment_picoc(stmt) + []
            case pn.Assign(pn.Alloc(_, _, pn.Name() as name) as alloc, exp):
                exps_mon = self._picoc_mon_exp(exp)
                self._picoc_mon_exp(alloc)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [pn.Assign(name, pn.Stack(pn.Num("1")))]
                )
            case pn.Assign(ref_loc, exp):
                # Deref, Subscript, Attribute
                exps_mon = self._picoc_mon_exp(exp)
                refs_mon = self._picoc_mon_ref(ref_loc, [])
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + refs_mon
                    + [pn.Assign(pn.Stack(pn.Num("1")), pn.Stack(pn.Num("2")))]
                )
            # --------------------- L_Assign_Alloc + L_Fun --------------------
            case pn.Exp(alloc_call):
                exps_mon = self._picoc_mon_exp(alloc_call)
                return self._single_line_comment_picoc(stmt) + exps_mon
            # ----------------------- L_If_Else + L_Loop ----------------------
            case pn.IfElse(exp, stmts1, stmts2):
                exps_mon = self._picoc_mon_exp(exp)
                stmts1_mon = []
                for stmt1 in stmts1:
                    stmts1_mon += self._picoc_mon_stmt(stmt1)
                stmts2_mon = []
                for stmt2 in stmts2:
                    stmts2_mon += self._picoc_mon_stmt(stmt2)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [pn.IfElse(pn.Stack(pn.Num("1")), stmts1_mon, stmts2_mon)]
                )
            # ----------------------------- L_Fun -----------------------------
            case pn.Return(exp):
                exps_mon = self._picoc_mon_exp(exp)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [pn.Return(pn.Stack(pn.Num("1")))]
                )
            # ---------------------------- L_Block ----------------------------
            case pn.GoTo():
                return [stmt]
            # --------------------------- L_Comment ---------------------------
            case pn.SingleLineComment():
                return [stmt]
            case _:
                bug_in_compiler(stmt)

    def _picoc_mon_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case pn.FunDef(datatype, pn.Name(val) as name, allocs, blocks):
                self.current_scope = val
                self.rel_fun_addr = 0
                blocks_mon = []
                for block in blocks:
                    match block:
                        case pn.Block(_, stmts):
                            stmts_mon = []
                            for stmt in stmts:
                                stmts_mon += self._picoc_mon_stmt(stmt)
                            block.stmts_instrs[:] = stmts_mon
                            blocks_mon += [block]
                        case _:
                            bug_in_compiler(block)
                return [pn.FunDef(datatype, name, allocs, blocks_mon)]
            case pn.FunDecl():
                # Function declaration isn't needed anymore after being evaluated
                return []
            case pn.StructDecl(pn.Name(val1, pos1), allocs):
                struct_name = val1
                attrs = []
                struct_size = 0
                if self.symbol_table.exists(struct_name):
                    symbol = self.symbol_table.resolve(struct_name)
                    match symbol:
                        case st.Symbol(
                            _,
                            _,
                            pn.Name(),
                            _,
                            st.Pos(pn.Num(pos_first_line), pn.Num(pos_first_column)),
                        ):
                            raise errors.Redeclaration(
                                val1,
                                pos1,
                                Pos(int(pos_first_line), int(pos_first_column)),
                            )
                        case _:
                            bug_in_compiler(symbol)
                for alloc in allocs:
                    match alloc:
                        case pn.Alloc(pn.Writeable(), datatype, pn.Name(val2, pos2)):
                            attr_name = val2
                            attr_size = self._datatype_size(datatype)
                            symbol = st.Symbol(
                                st.Empty(),
                                datatype,
                                pn.Name(f"{attr_name}@{struct_name}"),
                                st.Empty(),
                                st.Pos(
                                    pn.Num(str(pos2.line)), pn.Num(str(pos2.column))
                                ),
                                pn.Num(str(attr_size)),
                            )
                            self.symbol_table.define(symbol)
                            attrs += [pn.Name(f"{attr_name}@{struct_name}")]
                            struct_size += attr_size
                        case _:
                            bug_in_compiler(alloc)
                symbol = st.Symbol(
                    st.Empty(),
                    st.SelfDeclared(),
                    pn.Name(struct_name),
                    attrs,
                    st.Pos(pn.Num(str(pos1.line)), pn.Num(str(pos1.column))),
                    pn.Num(str(struct_size)),
                )
                self.symbol_table.define(symbol)
                # Struct declaration isn't needed anymore after being evaluated
                return []
            case _:
                bug_in_compiler(decl_def)

    def picoc_mon(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                decls_defs_mon = []
                for decl_def in decls_defs:
                    decls_defs_mon += self._picoc_mon_def(decl_def)
                return pn.File(
                    pn.Name(remove_extension(val) + ".picoc_mon"), decls_defs_mon
                )
            case _:
                bug_in_compiler(file)

    # =========================================================================
    # =                              RETI_Blocks                              =
    # =========================================================================

    def _single_line_comment_reti(self, stmt):
        if not (global_vars.args.verbose or global_vars.args.double_verbose):
            return []
        tmp = global_vars.args.double_verbose
        global_vars.args.double_verbose = True
        comment = [
            pn.SingleLineComment(
                "#",
                convert_to_single_line(stmt),
            )
        ]
        global_vars.args.double_verbose = tmp
        return comment

    def _reti_blocks_stmt(self, stmt):
        match stmt:
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
                        bug_in_compiler(bin_lop)
                return self._single_line_comment_reti(stmt) + [
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
                return self._single_line_comment_reti(stmt) + [
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
            case pn.Exp(pn.Name(val, pos)):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
                try:
                    symbol = self.symbol_table.resolve(f"{val}@{self.current_scope}")
                    choosen_scope = self.current_scope
                except KeyError:
                    # TODO: remove in case global variables won't be implemented
                    try:
                        symbol = self.symbol_table.resolve(f"{val}@global")
                        choosen_scope = "global"
                    except KeyError:
                        raise errors.UnknownIdentifier(val, pos)
                match symbol:
                    # TODO: anpassen an Nutzung von DS um nur Relativadressen zu nutzen
                    case st.Symbol(pn.Writeable(), _, _, pn.Num(val)):
                        match choosen_scope:
                            case ("main" | "global"):
                                reti_instrs += [
                                    rn.Instr(
                                        rn.Loadin(),
                                        [rn.Reg(rn.Ds()), rn.Reg(rn.Acc()), rn.Im(val)],
                                    )
                                ]
                            case _:
                                reti_instrs += [
                                    rn.Instr(
                                        rn.Loadin(),
                                        [
                                            rn.Reg(rn.Baf()),
                                            rn.Reg(rn.Acc()),
                                            rn.Im(str(-(2 + int(val)))),
                                        ],
                                    )
                                ]
                    case st.Symbol(pn.Const(), _, _, pn.Num(val)):
                        reti_instrs += [
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)]),
                        ]
                    case _:
                        bug_in_compiler(symbol)

                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            case (pn.Exp(pn.Num(val) as datatype) | pn.Exp(pn.Char(val) as datatype)):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                match datatype:
                    case pn.Num():
                        reti_instrs += [
                            rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)])
                        ]
                    case pn.Char():
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(str(ord(val)))]
                            )
                        ]
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
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
                        bug_in_compiler(bin_aop)
                return self._single_line_comment_reti(stmt) + [
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
                reti_instrs = self._single_line_comment_reti(stmt) + [
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
                        bug_in_compiler(un_op)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    )
                ]
            case pn.Exp(pn.Call(pn.Name("input"), [])):
                return self._single_line_comment_reti(stmt) + [
                    rn.Call(rn.Name("INPUT"), rn.Reg(rn.Acc())),
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            case pn.Exp(pn.Call(pn.Name("print"), [pn.Stack(pn.Num(val))])):
                return self._single_line_comment_reti(stmt) + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Call(rn.Name("PRINT"), rn.Reg(rn.Acc())),
                ]
            # ---------------------------- L_Logic ----------------------------
            case pn.Exp(pn.ToBool(pn.Stack(pn.Num(val)))):
                return self._single_line_comment_reti(stmt) + [
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
                        bug_in_compiler(rel)
                return self._single_line_comment_reti(stmt) + [
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
            case pn.Assign(pn.Name(val1, pos1), pn.Stack(pn.Num(val2))):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    rn.Instr(
                        rn.Loadin(),
                        [
                            rn.Reg(rn.Sp()),
                            rn.Reg(rn.Acc()),
                            rn.Im(val2),
                        ],
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
                try:
                    symbol = self.symbol_table.resolve(f"{val1}@{self.current_scope}")
                    choosen_scope = self.current_scope
                except KeyError:
                    # TODO: remove in case global variables won't be implemented
                    try:
                        symbol = self.symbol_table.resolve(f"{val1}@global")
                        choosen_scope = "global"
                    except KeyError:
                        raise errors.UnknownIdentifier(val1, pos1)
                # TODO: remove in case global variables won't be implemented
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, pn.Num(val3)):
                        match choosen_scope:
                            case ("main" | "global"):
                                return reti_instrs + [
                                    rn.Instr(
                                        rn.Storein(),
                                        [
                                            rn.Reg(rn.Ds()),
                                            rn.Reg(rn.Acc()),
                                            rn.Im(val3),
                                        ],
                                    ),
                                ]
                            case _:
                                return reti_instrs + [
                                    rn.Instr(
                                        rn.Storein(),
                                        [
                                            rn.Reg(rn.Baf()),
                                            rn.Reg(rn.Acc()),
                                            rn.Im(str(-(2 + int(val3)))),
                                        ],
                                    ),
                                ]
                    case st.Symbol(
                        pn.Const(),
                        _,
                        _,
                        _,
                        _,
                    ):
                        const_name = val1
                        const_pos = pos1
                        raise errors.ConstAssign(
                            const_name,
                            const_pos,
                        )
                    case _:
                        bug_in_compiler(symbol)
            case pn.Assign(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2))):
                return self._single_line_comment_reti(stmt) + [
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
            # ----------------------------- L_Pntr ----------------------------
            case pn.Exp(pn.Ref(pn.Name(val1, pos1))):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")])
                ]
                try:
                    symbol = self.symbol_table.resolve(f"{val1}@{self.current_scope}")
                    choosen_scope = self.current_scope
                except KeyError:
                    try:
                        symbol = self.symbol_table.resolve(f"{val1}@global")
                        choosen_scope = "global"
                    except KeyError:
                        raise errors.UnknownIdentifier(val1, pos1)
                match symbol:
                    case st.Symbol(pn.Writeable(), _, _, pn.Num(val2)):
                        match choosen_scope:
                            case ("main" | "global"):
                                reti_instrs += [
                                    rn.Instr(
                                        rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val2)]
                                    ),
                                    rn.Instr(
                                        rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Ds())]
                                    ),
                                ]
                            case _:
                                reti_instrs += [
                                    rn.Instr(
                                        rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.Acc())]
                                    ),
                                    rn.Instr(
                                        rn.Loadi(), [rn.Reg(rn.In2()), rn.Im(val2)]
                                    ),
                                    rn.Instr(
                                        rn.Sub(), [rn.Reg(rn.Acc()), rn.Reg(rn.In2())]
                                    ),
                                    rn.Instr(rn.Subi(), [rn.Reg(rn.Acc()), rn.Im("2")]),
                                ]
                    case st.Symbol(pn.Const()):
                        raise errors.ConstRef(val1, pos1)
                    case _:
                        bug_in_compiler(symbol)
                return reti_instrs + [
                    rn.Instr(
                        rn.Storein(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")],
                    )
                ]
            # TODO: remove after implementing Shrink Pass
            case pn.Exp(
                pn.Ref(
                    (
                        pn.Subscr(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2)))
                        | pn.Deref(pn.Stack(pn.Num(val1)), pn.Stack(pn.Num(val2)))
                    ),
                    datatype,
                    error_data,
                )
            ):
                #  __import__("pudb").set_trace()
                reti_instrs = self._single_line_comment_reti(stmt)
                match datatype:
                    case pn.ArrayDecl(nums, datatype2):
                        help_const = self._datatype_size(datatype2)
                        for num in nums[1:]:
                            match num:
                                case pn.Num(val3):
                                    help_const *= int(val3)
                                case _:
                                    bug_in_compiler(num)
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
                                        bug_in_compiler(datatype)
                            # bei z.B. Deref(deref_loc, Num("0")) wird für die
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
                                        bug_in_compiler(datatype)
                            case _:
                                bug_in_compiler(error_data)
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")]
                    ),
                ]
            case pn.Exp(
                pn.Ref(
                    pn.Attr(pn.Stack(pn.Num(val1)), pn.Name(val2, pos2)),
                    datatype,
                    error_data,
                )
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
                                            bug_in_compiler(symbol)
                                else:
                                    attr_pos = pos2
                                    raise errors.UnknownAttribute(
                                        attr_name, attr_pos, struct_name
                                    )
                            case _:
                                bug_in_compiler(symbol)
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
                                        bug_in_compiler(datatype)
                            case _:
                                bug_in_compiler(error_data)
                return self._single_line_comment_reti(stmt) + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.In1()), rn.Im(rel_pos_in_struct)]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("1")]
                    ),
                ]
            # TODO: remove after implementing Shrink Pass
            #  case pn.Exp(pn.Deref(deref_loc, exp)):
            #      reti_instrs = []
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case pn.Exp(pn.Subscr(pn.Stack(pn.Num(val1)), pn.Num("0"))):
                return self._single_line_comment_reti(stmt) + [
                    rn.Instr(
                        rn.Loadin(),
                        [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im(val1)],
                    ),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.In1()), rn.Reg(rn.Acc()), rn.Im("0")]
                    ),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im("1")]
                    ),
                ]
            case pn.Assign(
                pn.Memory(pn.Num(val1)) as mem, pn.Stack(pn.Num(val2)) as sta
            ):
                reti_instrs = []
                stack_offset = val2
                # TODO: remove in case global won't be implemented
                while True:
                    match (mem, sta):
                        case (_, pn.Stack(pn.Num("0"))):
                            break
                        case (pn.Memory(pn.Num(val1)), pn.Stack(pn.Num(val2))):
                            reti_instrs += self._single_line_comment_reti(stmt) + [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Sp()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(val2),
                                    ],
                                )
                            ]
                            match self.current_scope:
                                case "main":
                                    reti_instrs += [
                                        rn.Instr(
                                            rn.Storein(),
                                            [
                                                rn.Reg(rn.Ds()),
                                                rn.Reg(rn.Acc()),
                                                rn.Im(val1),
                                            ],
                                        ),
                                    ]
                                case _:
                                    reti_instrs += [
                                        rn.Instr(
                                            rn.Storein(),
                                            [
                                                rn.Reg(rn.Baf()),
                                                rn.Reg(rn.Acc()),
                                                rn.Im(str(-(2 + int(val2)))),
                                            ],
                                        ),
                                    ]
                        case _:
                            bug_in_compiler(mem, sta)
                    mem.num.val = str(int(mem.num.val) + 1)
                    sta.num.val = str(int(sta.num.val) - 1)
                return reti_instrs + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im(stack_offset)])
                ]
            # ---------------------------- L_Struct ---------------------------
            # TODO: remove after implementing Shrink Pass
            #  case pn.Exp(pn.Attr(ref_loc, name)):
            #  pass
            #  case pn.Assign(
            #      pn.Alloc(type_qual, datatype, pntr_decl), pn.Struct(assigns)
            #  ):
            #      pass
            # ----------------------- L_If_Else + L_Loop ----------------------
            case pn.IfElse(pn.Stack(pn.Num(val)), [goto1], [goto2]):
                return (
                    self._single_line_comment_reti(stmt)
                    + [
                        rn.Instr(
                            rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                        ),
                        rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                        rn.Jump(rn.Eq(), goto2),
                    ]
                    + self._single_line_comment_reti(goto1)
                    + [goto1]
                )
            # ----------------------------- L_Fun -----------------------------
            # TODO:
            #  case pn.Exp(pn.Call(name, exps)):
            #      return self._single_line_comment_reti(stmt) + [
            #          rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.Acc())]),
            #          rn.Instr(rn.Move(), [rn.Reg(rn.Sp()), rn.Reg(rn.Baf())]),
            #          rn.Instr(
            #              rn.Storein(), [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("0")]
            #          ),
            #          rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im("1")]),
            #          rn.Instr(
            #              rn.Storein(), [rn.Reg(rn.Baf()), rn.Reg(rn.Acc()), rn.Im("-1")]
            #          ),
            #      ]
            case pn.Return(pn.Stack(pn.Num(val))):
                return self._single_line_comment_reti(stmt) + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")]
                    ),
                ]
            # ---------------------------- L_Blocks ---------------------------
            case pn.GoTo():
                return self._single_line_comment_reti(stmt) + [stmt]
            # --------------------------- L_Comment ---------------------------
            case pn.SingleLineComment(prefix, content):
                match prefix:
                    case "//":
                        return [pn.SingleLineComment("# //", content)]
                    case _:
                        bug_in_compiler(prefix)
            case _:
                bug_in_compiler(stmt)

    def _reti_blocks_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case pn.FunDef(_, pn.Name(val), _, blocks):
                self.current_scope = val
                for block in blocks:
                    match block:
                        case pn.Block(_, stmts):
                            instrs = []
                            for stmt in stmts:
                                instrs += self._reti_blocks_stmt(stmt)
                            block.stmts_instrs[:] = instrs
                        case _:
                            bug_in_compiler(block)
                    # this has to be done in this pass, because the reti_blocks
                    # pass sometimes needs to access this attribute from a block
                    # where it hasn't yet beeen determined
                    # TODO: Move this into the patch_instructions pass, because
                    # in this pass goto(next_block_name) gets removed
                    block.instrs_before = pn.Num(str(self.instrs_cnt))
                    num_instrs = len(list(filter_out_comments(block.stmts_instrs)))
                    block.num_instrs = pn.Num(str(num_instrs))
                    block.visible += (
                        [block.instrs_before, block.num_instrs]
                        if global_vars.args.double_verbose
                        else []
                    )
                    self.instrs_cnt += num_instrs
                return blocks
            case _:
                bug_in_compiler(decl_def)

    def reti_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                reti_blocks = []
                for decl_def in decls_defs:
                    reti_blocks += self._reti_blocks_def(decl_def)
                return pn.File(
                    pn.Name(remove_extension(val) + ".reti_blocks"), reti_blocks
                )
            case _:
                bug_in_compiler(file)

    # =========================================================================
    # =                               RETI_Patch                              =
    # =========================================================================
    # - deal with large immediates
    # - deal with goto directly to next block
    # - deal with division by 0

    # =========================================================================
    # =                                  RETI                                 =
    # =========================================================================
    def _determine_distance(self, current_block, other_block, idx):
        if int(other_block.instrs_before.val) < int(current_block.instrs_before.val):
            return -(
                int(current_block.instrs_before.val)
                - int(other_block.instrs_before.val)
                + idx
            )
        elif int(other_block.instrs_before.val) == int(current_block.instrs_before.val):
            return -idx
        else:  # int(current_block.instrs_before.val) < int(other_block.instrs_before.val):
            return (
                int(other_block.instrs_before.val)
                - (
                    int(current_block.instrs_before.val)
                    + int(current_block.num_instrs.val)
                )
                + (int(current_block.num_instrs.val) - idx)
            )

    def _reti_instr(self, instr, idx, current_block):
        match instr:
            case pn.GoTo(pn.Name(val)):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return [rn.Jump(rn.Always(), rn.Im(str(distance)))]
            case rn.Jump(rn.Eq(), pn.GoTo(pn.Name(val))):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return self._single_line_comment_reti(instr) + [
                    rn.Jump(rn.Eq(), rn.Im(str(distance)))
                ]
            case _:
                return [instr]

    def _reti_block(self, block: pn.Block):
        match block:
            case pn.Block(_, instrs):
                instrs_block_free = []
                idx = 0
                for instr in instrs:
                    instrs_block_free += self._reti_instr(instr, idx, block)
                    match instr:
                        case pn.SingleLineComment():
                            pass
                        case _:
                            idx += 1
                return instrs_block_free
            case _:
                bug_in_compiler(block)

    def reti(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), blocks):
                instrs_block_free = []
                for block in blocks:
                    instrs_block_free += self._reti_block(block)
                return rn.Program(
                    rn.Name(remove_extension(val) + ".reti"), instrs_block_free
                )
            case _:
                bug_in_compiler(file)
