from picoc_nodes import N as PN
from reti_nodes import N as RN
from errors import Errors
from symbol_table import ST
from global_funs import bug_in_compiler, remove_extension, filter_out_comments, convert_to_single_line
from global_classes import Pos
import global_vars


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
        self.symbol_table = ST.SymbolTable()

    # =========================================================================
    # =                              PicoC_Shrink                             =
    # =========================================================================
    # =========================================================================
    # =                              PicoC_Blocks                             =
    # =========================================================================

    def _single_line_comment_picoc(self, stmt):
        if not global_vars.args.verbose:
            return []
        visibl_emptied_lists = list(
            map(lambda node: [] if isinstance(node, list) else node, stmt.visible)
        )
        stmt.visible = visibl_emptied_lists
        return [
            PN.SingleLineComment(
                "//",
                convert_to_single_line(stmt)
            )
        ]

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = PN.Block(
            PN.Name(label),
            self._single_line_comment_picoc(PN.Block(PN.Name(label), [])) + stmts,
        )
        blocks[label] = new_block
        self.block_id += 1
        return PN.GoTo(PN.Name(label))

    def _picoc_blocks_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            # --------------------------- L_If_Else ---------------------------
            case PN.If(exp, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_if = [goto_after]
                for sub_stmt in reversed(stmts):
                    stmts_if = self._picoc_blocks_stmt(sub_stmt, stmts_if, blocks)
                goto_if = self._create_block("if", stmts_if, blocks)

                return self._single_line_comment_picoc(stmt) + [
                    PN.IfElse(exp, [goto_if], [goto_after])
                ]
            case PN.IfElse(exp, stmts1, stmts2):
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
                    PN.IfElse(exp, [goto_if], [goto_else])
                ]
            # ----------------------------- L_Loop ----------------------------
            case PN.While(exp, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                goto_condition_check = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for sub_stmt in reversed(stmts):
                    stmts_while = self._picoc_blocks_stmt(sub_stmt, stmts_while, blocks)
                goto_branch.name.val = self._create_block(
                    "while_branch", stmts_while, blocks
                ).name.val

                condition_check = [PN.IfElse(exp, [goto_branch], [goto_after])]
                goto_condition_check.name.val = self._create_block(
                    "condition_check", condition_check, blocks
                ).name.val

                return self._single_line_comment_picoc(stmt) + [goto_condition_check]
            case PN.DoWhile(exp, stmts):
                goto_after = self._create_block(
                    "do_while_after", processed_stmts, blocks
                )

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [PN.IfElse(exp, [goto_branch], [goto_after])]

                for sub_stmt in reversed(stmts):
                    stmts_while = self._picoc_blocks_stmt(sub_stmt, stmts_while, blocks)
                goto_branch.name.val = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).name.val

                return self._single_line_comment_picoc(stmt) + [goto_branch]
            # ----------------------------- L_Fun -----------------------------
            case PN.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_blocks_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case PN.FunDef(datatype, PN.Name(fun_name) as name, params, stmts):
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
                    PN.FunDef(
                        datatype,
                        name,
                        params,
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
            case (PN.FunDecl() | PN.StructDecl()):
                return [decl_def]
            case _:
                bug_in_compiler(decl_def)

    def picoc_blocks(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(PN.Name(val), decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += self._picoc_blocks_def(decl_def)
                return PN.File(
                    PN.Name(remove_extension(val) + ".picoc_blocks"), decls_defs_blocks
                )
            case _:
                bug_in_compiler(file)

    # =========================================================================
    # =                               PicoC_Mon                               =
    # =========================================================================
    def _datatype_size(self, datatype):
        match datatype:
            # ------------------------ L_Arith + L_Pntr -----------------------
            case (PN.IntType() | PN.CharType() | PN.PntrDecl()):
                return 1
            # ---------------------------- L_Struct ---------------------------
            case PN.StructSpec(PN.Name(val)):
                symbol = self.symbol_table.resolve(val)
                match symbol:
                    case ST.Symbol(_, _, _, _, _, PN.Num(val)):
                        return int(val)
                    case _:
                        bug_in_compiler(symbol)
            # ---------------------------- L_Array ----------------------------
            case PN.ArrayDecl(nums, datatype2):
                size = self._datatype_size(datatype2)
                for num in nums:
                    match num:
                        case PN.Name(val):
                            size *= val
                        case _:
                            bug_in_compiler(num)
                return size
            case _:
                bug_in_compiler(datatype)

    def _picoc_mon_ref(self, ref_loc, prev_refs):
        match ref_loc:
            # ---------------------------- L_Arith ----------------------------
            case PN.Name(val):
                var_name = val
                symbol = self.symbol_table.resolve(f"{var_name}@{self.current_scope}")
                match symbol:
                    case ST.Symbol(_, datatype):
                        current_datatype = datatype
                    case _:
                        bug_in_compiler(symbol)
                while prev_refs:
                    match current_datatype:
                        case (PN.CharType() | PN.IntType()):
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            ref.chidlren += [ref.datatype]
                            break
                        case PN.PntrDecl(PN.Num(val), datatype):
                            if int(val) == 0:
                                current_datatype = datatype
                            current_datatype.num.val = int(val) - 1
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            ref.chidlren += [ref.datatype]
                        case PN.ArrayDecl(nums, datatype):
                            if len(nums) == 0:
                                current_datatype = datatype
                            current_datatype.nums = nums[1:]
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            ref.chidlren += [ref.datatype]
                        case PN.StructSpec(PN.Name(val1)):
                            struct_name = val1
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            ref.chidlren += [ref.datatype]
                            match ref:
                                case PN.Ref(PN.Attr(ref_loc, PN.Name(val2))):
                                    attr_name = val2
                                    symbol = self.symbol_table.resolve(
                                        f"{attr_name}@{struct_name}"
                                    )
                                case _:
                                    # TODO: here belongs a proper error message
                                    # nachsehen, ob [] auf Structvariable anwendbar ist
                                    bug_in_compiler(ref)
                            match symbol:
                                case ST.Symbol(_, datatype):
                                    current_datatype = datatype
                                case _:
                                    bug_in_compiler(symbol)
                        case _:
                            bug_in_compiler(current_datatype)
                return [PN.Exp(PN.Ref(ref_loc))]
            # ----------------------------- L_Pntr ----------------------------
            # TODO: remove after implementing shrink pass
            #  case PN.Deref(deref_loc, exp):
            #      ref = PN.Ref(ref_loc)
            #      refs_mon = self._picoc_mon_ref(deref_loc, [ref] + prev_refs)
            #      exps_mon = self._picoc_mon_exp(exp)
            #      return refs_mon + exps_mon + [PN.Exp(ref)]
            # ---------------------------- L_Array ----------------------------
            case PN.Subscr(deref_loc, exp):
                ref = PN.Ref(PN.Subscr(PN.Stack(PN.Num("2")), PN.Stack(PN.Num("1"))))
                refs_mon = self._picoc_mon_ref(deref_loc, [ref] + prev_refs)
                exps_mon = self._picoc_mon_exp(exp)
                return refs_mon + exps_mon + [PN.Exp(ref)]
            # ---------------------------- L_Struct ---------------------------
            case PN.Attr(ref_loc2, name):
                ref = PN.Ref(PN.Attr(PN.Stack(PN.Num("1")), name))
                refs_mon = self._picoc_mon_ref(ref_loc2, [ref] + prev_refs)
                return refs_mon + [PN.Exp(ref)]
            case _:
                bug_in_compiler(ref_loc)

    def _picoc_mon_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case (PN.Name() | PN.Num() | PN.Char()):
                return [PN.Exp(exp)]
            # ----------------------- L_Arith + L_Logic -----------------------
            case PN.BinOp(left_exp, bin_op, right_exp):
                exps1_mon = self._picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        PN.Exp(
                            PN.BinOp(
                                PN.Stack(PN.Num("2")), bin_op, PN.Stack(PN.Num("1"))
                            )
                        )
                    ]
                )
            case PN.UnOp(un_op, exp):
                exps_mon = self._picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.UnOp(un_op, PN.Stack(PN.Num("1"))))]
            # ---------------------------- L_Logic ----------------------------
            case PN.Atom(left_exp, rel, right_exp):
                exps1_mon = self._picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        PN.Exp(
                            PN.Atom(PN.Stack(PN.Num("2")), rel, PN.Stack(PN.Num("1")))
                        )
                    ]
                )
            case PN.ToBool(exp):
                exps_mon = self._picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.ToBool(PN.Stack(PN.Num("1"))))]
            # ------------------------- L_Assign_Alloc ------------------------
            case PN.Alloc(type_qual, datatype, PN.Name(val, pos)):
                var_name = val
                size = self._datatype_size(datatype)
                match self.current_scope:
                    case "main":
                        symbol = ST.Symbol(
                            type_qual,
                            datatype,
                            PN.Name(f"{var_name}@{self.current_scope}"),
                            PN.Num(str(self.rel_global_addr)),
                            ST.Pos(PN.Num(str(pos.line)), PN.Num(str(pos.column))),
                            PN.Num(str(size)),
                        )
                        self.symbol_table.define(symbol)
                        self.rel_global_addr += size
                    case _:
                        symbol = ST.Symbol(
                            type_qual,
                            datatype,
                            PN.Name(f"{var_name}@{self.current_scope}"),
                            PN.Num(str(self.rel_fun_addr)),
                            ST.Pos(PN.Num(str(pos.line)), PN.Num(str(pos.column))),
                            PN.Num(str(size)),
                        )
                        self.symbol_table.define(symbol)
                        self.rel_fun_addr += size
                # Alloc isn't needed anymore after being evaluated
                return []
            # ----------------------------- L_Pntr ----------------------------
            case PN.Ref(PN.Name()):
                return [PN.Exp(exp)]
            # TODO: remove Deref after Shrink Pass is implemented
            case PN.Ref((PN.Subscr() | PN.Attr() | PN.Deref()) as ref_loc):
                return self._picoc_mon_ref(ref_loc, [])
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            # TODO: remove after Shrink Pass is implemented
            case (PN.Subscr() | PN.Attr() | PN.Deref()):
                refs_mon = self._picoc_mon_ref(exp, [])
                return refs_mon + [PN.Exp(PN.Subscr(PN.Stack(PN.Num("1")), RN.Im("0")))]
            # ----------------------------- L_Fun -----------------------------
            case PN.Call(name, exps):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon += self._picoc_mon_exp(exp)
                    stack_locs[0:0] = [PN.Stack(PN.Num(str(i + 1)))]
                return exps_mon + [PN.Exp(PN.Call(name, stack_locs))]
            case _:
                bug_in_compiler(exp)

    def _picoc_mon_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
            case PN.Assign(PN.Name() as name, exp):
                exps_mon = self._picoc_mon_exp(exp)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [PN.Assign(name, PN.Stack(PN.Num("1")))]
                )
            case PN.Assign(
                PN.Alloc(PN.Const() as type_qual, datatype, PN.Name(val1, pos)), num
            ):
                var_name = val1
                symbol = ST.Symbol(
                    type_qual,
                    datatype,
                    PN.Name(f"{var_name}@{self.current_scope}"),
                    num,
                    ST.Pos(PN.Num(str(pos.line)), PN.Num(str(pos.column))),
                    ST.Empty(),
                )
                self.symbol_table.define(symbol)
                # Alloc isn't needed anymore after being evaluated
                return self._single_line_comment_picoc(stmt) + []
            case PN.Assign(PN.Alloc(_, _, PN.Name() as name) as alloc, exp):
                exps1_mon = self._picoc_mon_exp(exp)
                exps2_mon = self._picoc_mon_exp(alloc)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps1_mon
                    + exps2_mon
                    + [PN.Assign(name, PN.Stack(PN.Num("1")))]
                )
            case PN.Assign(ref_loc, exp):
                # Deref, Subscript, Attribute
                exps_mon = self._picoc_mon_exp(exp)
                refs_mon = self._picoc_mon_ref(ref_loc, [])
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + refs_mon
                    + [PN.Assign(PN.Stack(PN.Num("1")), PN.Stack(PN.Num("2")))]
                )
            # --------------------- L_Assign_Alloc + L_Fun --------------------
            case PN.Exp(alloc_call):
                exps_mon = self._picoc_mon_exp(alloc_call)
                return self._single_line_comment_picoc(stmt) + exps_mon
            # ---------------------------- L_Array ----------------------------
            case PN.Assign(PN.Alloc(_, _, _) as alloc, PN.Array(exps)):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon += self._picoc_mon_exp(exp)
                    stack_locs[0:0] = [PN.Stack(PN.Num(str(i + 1)))]
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [PN.Assign(alloc, PN.Array(stack_locs))]
                )
            # ---------------------------- L_Struct ---------------------------
            case PN.Assign(PN.Alloc(_, _, _) as alloc, PN.Struct(assigns)):
                exps_mon = []
                assigns_mon = []
                for i, assign in enumerate(assigns):
                    match assign:
                        case PN.Assign(assign_lhs, exp):
                            exps_mon += self._picoc_mon_exp(exp)
                            assigns_mon[0:0] = [
                                PN.Assign(assign_lhs, PN.Stack(PN.Num(i + 1)))
                            ]
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [PN.Assign(alloc, PN.Struct(assigns_mon))]
                )
            # ----------------------- L_If_Else + L_Loop ----------------------
            case PN.IfElse(exp, stmts1, stmts2):
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
                    + [PN.IfElse(PN.Stack(PN.Num("1")), stmts1_mon, stmts2_mon)]
                )
            # ----------------------------- L_Fun -----------------------------
            case PN.Return(exp):
                exps_mon = self._picoc_mon_exp(exp)
                return (
                    self._single_line_comment_picoc(stmt)
                    + exps_mon
                    + [PN.Return(PN.Stack(PN.Num("1")))]
                )
            # ---------------------------- L_Block ----------------------------
            case PN.GoTo():
                return [stmt]
            # --------------------------- L_Comment ---------------------------
            case PN.SingleLineComment():
                return [stmt]
            case _:
                bug_in_compiler(stmt)

    def _picoc_mon_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case PN.FunDef(datatype, PN.Name(val) as name, params, blocks):
                self.current_scope = val
                self.rel_fun_addr = 0
                blocks_mon = []
                for block in blocks:
                    match block:
                        case PN.Block(_, stmts):
                            stmts_mon = []
                            for stmt in stmts:
                                stmts_mon += self._picoc_mon_stmt(stmt)
                            block.stmts_instrs[:] = stmts_mon
                            blocks_mon += [block]
                        case _:
                            bug_in_compiler(block)
                return [PN.FunDef(datatype, name, params, blocks_mon)]
            case PN.FunDecl():
                # Function declaration isn't needed anymore after being evaluated
                return []
            case PN.StructDecl(PN.Name(val1, pos1), params):
                struct_name = val1
                attrs = []
                struct_size = 0
                for param in params:
                    match param:
                        case PN.Param(datatype, PN.Name(val2, pos2)):
                            attr_name = val2
                            attr_size = self._datatype_size(datatype)
                            symbol = ST.Symbol(
                                ST.Empty(),
                                datatype,
                                PN.Name(f"{attr_name}@{struct_name}"),
                                ST.Pos(
                                    PN.Num(str(pos2.line)), PN.Num(str(pos2.column))
                                ),
                                PN.Num(str(attr_size)),
                            )
                            self.symbol_table.define(symbol)
                            attrs += [PN.Name(f"{attr_name}@{struct_name}")]
                            struct_size += attr_size
                        case _:
                            bug_in_compiler(param)
                symbol = ST.Symbol(
                    ST.Empty(),
                    ST.SelfDeclared(),
                    PN.Name(struct_name),
                    attrs,
                    ST.Pos(PN.Num(str(pos1.line)), PN.Num(str(pos1.column))),
                    PN.Num(str(struct_size)),
                )
                self.symbol_table.define(symbol)
                # Struct declaration isn't needed anymore after being evaluated
                return []
            case _:
                bug_in_compiler(decl_def)

    def picoc_mon(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(PN.Name(val), decls_defs):
                decls_defs_mon = []
                for decl_def in decls_defs:
                    decls_defs_mon += self._picoc_mon_def(decl_def)
                return PN.File(
                    PN.Name(remove_extension(val) + ".picoc_mon"), decls_defs_mon
                )
            case _:
                bug_in_compiler(file)

    # =========================================================================
    # =                              RETI_Blocks                              =
    # =========================================================================

    def _single_line_comment_reti(self, stmt):
        if not global_vars.args.verbose:
            return []
        return [
            PN.SingleLineComment(
                "#",
                convert_to_single_line(stmt),
            )
        ]

    def _reti_blocks_stmt(self, stmt):
        match stmt:
            # ---------------------------- L_Logic ----------------------------
            case PN.Exp(
                PN.BinOp(
                    PN.Stack(PN.Num(val1)),
                    (PN.LogicAnd() | PN.LogicOr()) as bin_lop,
                    PN.Stack(PN.Num(val2)),
                )
            ):
                match bin_lop:
                    case PN.LogicAnd():
                        lop = RN.And()
                    case PN.LogicOr():
                        lop = RN.Or()
                    case _:
                        bug_in_compiler(bin_lop)
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val1)]
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val2)]
                    ),
                    RN.Instr(lop, [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("2")]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                ]
            case PN.Exp(PN.UnOp(PN.LogicNot(), PN.Stack(PN.Num(val)))):
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im("1")]),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val)]
                    ),
                    RN.Instr(RN.Oplus(), [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            # ---------------------------- L_Arith ----------------------------
            case PN.Exp(PN.Name(val, pos)):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
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
                        raise Errors.UnknownIdentifier(val, pos)
                match symbol:
                    # TODO: anpassen an Nutzung von DS um nur Relativadressen zu nutzen
                    case ST.Symbol(PN.Writeable(), _, _, PN.Num(val)):
                        match choosen_scope:
                            case ("main" | "global"):
                                reti_instrs += [
                                    RN.Instr(
                                        RN.Loadin(),
                                        [RN.Reg(RN.Ds()), RN.Reg(RN.Acc()), RN.Im(val)],
                                    )
                                ]
                            case _:
                                reti_instrs += [
                                    RN.Instr(
                                        RN.Loadin(),
                                        [
                                            RN.Reg(RN.Baf()),
                                            RN.Reg(RN.Acc()),
                                            RN.Im(str(-(2 + int(val)))),
                                        ],
                                    )
                                ]
                    case ST.Symbol(PN.Const(), _, _, PN.Num(val)):
                        reti_instrs += [
                            RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im(val)]),
                        ]
                    case _:
                        bug_in_compiler(symbol)

                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            case (PN.Exp(PN.Num(val) as datatype) | PN.Exp(PN.Char(val) as datatype)):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")])
                ]
                match datatype:
                    case PN.Num():
                        reti_instrs += [
                            RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im(val)])
                        ]
                    case PN.Char():
                        reti_instrs += [
                            RN.Instr(
                                RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im(str(ord(val)))]
                            )
                        ]
                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            case PN.Exp(
                PN.BinOp(PN.Stack(PN.Num(val1)), bin_aop, PN.Stack(PN.Num(val2)))
            ):
                match bin_aop:
                    case PN.Add():
                        aop = RN.Add()
                    case PN.Sub():
                        aop = RN.Sub()
                    case PN.Mul():
                        aop = RN.Mult()
                    case PN.Div():
                        aop = RN.Div()
                    case PN.Mod():
                        aop = RN.Mod()
                    case PN.Oplus():
                        aop = RN.Oplus()
                    case PN.And():
                        aop = RN.And()
                    case PN.Or():
                        aop = RN.Or()
                    case _:
                        bug_in_compiler(bin_aop)
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val1)]
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val2)]
                    ),
                    RN.Instr(aop, [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("2")]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                ]
            case PN.Exp(PN.UnOp(un_op, PN.Stack(PN.Num(val)))):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im("0")]),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val)]
                    ),
                    RN.Instr(RN.Sub(), [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                ]
                match un_op:
                    case PN.Not():
                        reti_instrs += [
                            RN.Instr(RN.Subi(), [RN.Reg(RN.Acc()), RN.Im("1")])
                        ]
                    case PN.Minus():
                        pass
                    case _:
                        bug_in_compiler(un_op)
                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    )
                ]
            case PN.Exp(PN.Call(PN.Name("input"), [])):
                return self._single_line_comment_reti(stmt) + [
                    RN.Call(RN.Name("INPUT"), RN.Reg(RN.Acc())),
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            case PN.Exp(PN.Call(PN.Name("print"), [PN.Stack(PN.Num(val))])):
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val)]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                    RN.Call(RN.Name("PRINT"), RN.Reg(RN.Acc())),
                ]
            # ---------------------------- L_Logic ----------------------------
            case PN.Exp(PN.ToBool(PN.Stack(PN.Num(val)))):
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                    RN.Jump(RN.Eq(), RN.Im("3")),
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im("1")]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val)]
                    ),
                ]
            case PN.Exp(PN.Atom(PN.Stack(PN.Num(val1)), rel, PN.Stack(PN.Num(val2)))):
                match rel:
                    case PN.Eq():
                        rel = RN.Eq()
                    case PN.NEq():
                        rel = RN.NEq()
                    case PN.Lt():
                        rel = RN.Lt()
                    case PN.LtE():
                        rel = RN.LtE()
                    case PN.Gt():
                        rel = RN.Gt()
                    case PN.GtE():
                        rel = RN.GtE()
                    case _:
                        bug_in_compiler(rel)
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val1)]
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val2)]
                    ),
                    RN.Instr(RN.Sub(), [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                    RN.Jump(rel, RN.Im("3")),
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im("0")]),
                    RN.Jump(RN.Always(), RN.Im("2")),
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im("1")]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("2")]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                ]
            # ------------------------- L_Assign_Alloc ------------------------
            case PN.Assign(PN.Name(val1, pos1), PN.Stack(PN.Num(val2))):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(),
                        [
                            RN.Reg(RN.Sp()),
                            RN.Reg(RN.Acc()),
                            RN.Im(val2),
                        ],
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
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
                        raise Errors.UnknownIdentifier(val1, pos1)
                # TODO: remove in case global variables won't be implemented
                match symbol:
                    case ST.Symbol(PN.Writeable(), _, _, PN.Num(val3)):
                        match choosen_scope:
                            case ("main" | "global"):
                                return reti_instrs + [
                                    RN.Instr(
                                        RN.Storein(),
                                        [
                                            RN.Reg(RN.Ds()),
                                            RN.Reg(RN.Acc()),
                                            RN.Im(val3),
                                        ],
                                    ),
                                ]
                            case _:
                                return reti_instrs + [
                                    RN.Instr(
                                        RN.Storein(),
                                        [
                                            RN.Reg(RN.Baf()),
                                            RN.Reg(RN.Acc()),
                                            RN.Im(str(-(2 + int(val3)))),
                                        ],
                                    ),
                                ]
                    case ST.Symbol(
                        PN.Const(),
                        _,
                        _,
                        _,
                        ST.Pos(PN.Num(line), PN.Num(column)),
                    ):
                        const_name = val1
                        const_pos = pos1
                        raise Errors.ConstReassignment(
                            const_name,
                            const_pos,
                            Pos(int(line), int(column)),
                        )
                    case _:
                        bug_in_compiler(symbol)
            case PN.Assign(PN.Stack(PN.Num(val1)), PN.Stack(PN.Num(val2))):
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im(val1)]
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val2)]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("2")]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.In1()), RN.Reg(RN.Acc()), RN.Im("0")]
                    ),
                ]
            # ----------------------------- L_Pntr ----------------------------
            case PN.Exp(PN.Ref(PN.Name(val1, pos1))):
                reti_instrs = self._single_line_comment_reti(stmt) + [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")])
                ]
                try:
                    symbol = self.symbol_table.resolve(f"{val1}@{self.current_scope}")
                    choosen_scope = self.current_scope
                except KeyError:
                    try:
                        symbol = self.symbol_table.resolve(f"{val1}@global")
                        choosen_scope = "global"
                    except KeyError:
                        raise Errors.UnknownIdentifier(val1, pos1)
                match symbol:
                    case ST.Symbol(PN.Writeable(), _, _, PN.Num(val2)):
                        match choosen_scope:
                            case ("main", "global"):
                                reti_instrs += [
                                    RN.Instr(
                                        RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im(val2)]
                                    ),
                                    RN.Instr(
                                        RN.Add(), [RN.Reg(RN.Acc()), RN.Reg(RN.Ds())]
                                    ),
                                ]
                            case _:
                                reti_instrs += [
                                    RN.Instr(
                                        RN.Move(), [RN.Reg(RN.Baf()), RN.Reg(RN.Acc())]
                                    ),
                                    RN.Instr(
                                        RN.Loadi(), [RN.Reg(RN.In2()), RN.Im(val2)]
                                    ),
                                    RN.Instr(
                                        RN.Sub(), [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]
                                    ),
                                    RN.Instr(RN.Subi(), [RN.Reg(RN.Acc()), RN.Im("2")]),
                                ]
                    case ST.Symbol(PN.Const()):
                        raise Errors.ConstRef(val1, pos1)
                    case _:
                        bug_in_compiler(symbol)
                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(),
                        [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")],
                    )
                ]
            # TODO: remove after implementing Shrink Pass
            case PN.Exp(
                PN.Ref(
                    (
                        PN.Subscr(PN.Stack(PN.Num(val1)), PN.Stack(PN.Num(val2)))
                        | PN.Deref(PN.Stack(PN.Num(val1)), PN.Stack(PN.Num(val2)))
                    ),
                    datatype,
                )
            ):
                reti_instrs = self._single_line_comment_reti(stmt)
                match datatype:
                    case PN.ArrayDecl(nums, datatype2):
                        help_const = self._datatype_size(datatype2)
                        for num in nums:
                            match num:
                                case PN.Num(val3):
                                    help_const *= int(val3)
                                case _:
                                    bug_in_compiler(num)
                        reti_instrs += [
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im(val1)],
                            ),
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val2)],
                            ),
                            RN.Instr(
                                RN.Multi(), [RN.Reg(RN.In2()), RN.Im(str(help_const))]
                            ),
                            RN.Instr(RN.Add(), [RN.Reg(RN.In1()), RN.Reg(RN.In2())]),
                        ]
                    case PN.PntrDecl(_, datatype2):
                        help_const = self._datatype_size(datatype2)
                        reti_instrs += [
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val1)],
                            ),
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.In2()), RN.Reg(RN.In1()), RN.Im("0")],
                            ),
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Im(val2)],
                            ),
                            RN.Instr(
                                RN.Multi(), [RN.Reg(RN.In2()), RN.Im(str(help_const))]
                            ),
                            RN.Instr(RN.Add(), [RN.Reg(RN.In1()), RN.Reg(RN.In2())]),
                        ]
                    case PN.StructSpec(PN.Name(val)):
                        raise Errors.DatatypeMismatch(val, pos, f"struct {val}", "array or pointer")
                    case PN.PntrDecl():
                        pass
                    case PN.IntType():
                        raise Errors.DatatypeMismatch(, , "int", "array or pointer")
                    case PN.CharType():
                        pass
                    case _:
                return reti_instrs + [
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im("1")]
                    ),
                ]
            case PN.Exp(
                PN.Ref(PN.Attr(PN.Stack(PN.Num(val1)), PN.Name(val2, pos2)), datatype)
            ):
                attr_name = val2
                rel_pos_in_struct = 0
                match datatype:
                    case PN.StructSpec(PN.Name(val3)):
                        # determine relative pos in struct
                        struct_name = val3
                        symbol = self.symbol_table.resolve(struct_name)
                        # TODO: try error and error message
                        match symbol:
                            case ST.Symbol(_, _, _, val4):
                                attr_ids = val4
                                for attr_id in attr_ids:
                                    if attr_id.val == f"{attr_name}@{struct_name}":
                                        break
                                    symbol = self.symbol_table.resolve(attr_id.val)
                                    match symbol:
                                        case ST.Symbol(_, _, _, _, _, PN.Num(val4)):
                                            attr_size = val4
                                            rel_pos_in_struct += int(attr_size)
                                        case _:
                                            bug_in_compiler(symbol)
                                else:
                                    attr_pos = pos2
                                    raise Errors.UnknownAttribute(
                                        attr_name, attr_pos, struct_name
                                    )
                            case _:
                                bug_in_compiler(symbol)
                    case _:
                        raise Errors.DatatypeMismatch()
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im(val1)]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.In1()), RN.Im(rel_pos_in_struct)]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im("1")]
                    ),
                ]
            # TODO: remove after implementing Shrink Pass
            #  case PN.Exp(PN.Deref(deref_loc, exp)):
            #      reti_instrs = []
            # ------------------ L_Pntr + L_Array + L_Struct ------------------
            case PN.Exp(PN.Subscr(PN.Stack(PN.Num("1")), PN.Num("0"))):
                return self._single_line_comment_reti(stmt) + [
                    RN.Instr(
                        RN.Loadin(),
                        [RN.Reg(RN.Sp()), RN.Reg(RN.In1()), RN.Im("1")],
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.In1()), RN.Reg(RN.Acc()), RN.Im("0")]
                    ),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            #  case PN.Assign(PN.Alloc(type_qual, datatype, pntr_decl), PN.Array(exps)):
            #      pass
            # ---------------------------- L_Struct ---------------------------
            # TODO: remove after implementing Shrink Pass
            #  case PN.Exp(PN.Attr(ref_loc, name)):
            #  pass
            #  case PN.Assign(
            #      PN.Alloc(type_qual, datatype, pntr_decl), PN.Struct(assigns)
            #  ):
            #      pass
            # ----------------------- L_If_Else + L_Loop ----------------------
            case PN.IfElse(PN.Stack(PN.Num(val)), [goto1], [goto2]):
                return (
                    self._single_line_comment_reti(stmt)
                    + [
                        RN.Instr(
                            RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val)]
                        ),
                        RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                        RN.Jump(RN.Eq(), goto2),
                    ]
                    + self._single_line_comment_reti(goto1)
                    + [goto1]
                )
            # ----------------------------- L_Fun -----------------------------
            #  case PN.Exp(PN.Call(identifier, exps)):
            #      pass
            #  case PN.Return(exp):
            #      pass
            # ---------------------------- L_Blocks ---------------------------
            case PN.GoTo():
                return self._single_line_comment_reti(stmt) + [stmt]
            # --------------------------- L_Comment ---------------------------
            case PN.SingleLineComment(prefix, content):
                match prefix:
                    case "//":
                        return [PN.SingleLineComment("# //", content)]
                    case _:
                        bug_in_compiler(prefix)
            case _:
                bug_in_compiler(stmt)

    def _reti_blocks_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case PN.FunDef(_, PN.Name(val), _, blocks):
                self.current_scope = val
                for block in blocks:
                    match block:
                        case PN.Block(_, stmts):
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
                    block.instrs_before = PN.Num(str(self.instrs_cnt))
                    num_instrs = len(list(filter_out_comments(block.stmts_instrs)))
                    block.num_instrs = PN.Num(str(num_instrs))
                    block.visible += [block.instrs_before, block.num_instrs]
                    self.instrs_cnt += num_instrs
                return blocks
            case _:
                bug_in_compiler(decl_def)

    def reti_blocks(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(PN.Name(val), decls_defs):
                reti_blocks = []
                for decl_def in decls_defs:
                    reti_blocks += self._reti_blocks_def(decl_def)
                return PN.File(
                    PN.Name(remove_extension(val) + ".reti_blocks"), reti_blocks
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
            case PN.GoTo(PN.Name(val)):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return [RN.Jump(RN.Always(), RN.Im(str(distance)))]
            case RN.Jump(RN.Eq(), PN.GoTo(PN.Name(val))):
                other_block = self.all_blocks[val]
                distance = self._determine_distance(current_block, other_block, idx)
                return self._single_line_comment_reti(instr) + [
                    RN.Jump(RN.Eq(), RN.Im(str(distance)))
                ]
            case _:
                return [instr]

    def _reti_block(self, block: PN.Block):
        match block:
            case PN.Block(_, instrs):
                instrs_block_free = []
                idx = 0
                for instr in instrs:
                    instrs_block_free += self._reti_instr(instr, idx, block)
                    match instr:
                        case PN.SingleLineComment():
                            pass
                        case _:
                            idx += 1
                return instrs_block_free
            case _:
                bug_in_compiler(block)

    def reti(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(PN.Name(val), blocks):
                instrs_block_free = []
                for block in blocks:
                    instrs_block_free += self._reti_block(block)
                return RN.Program(
                    RN.Name(remove_extension(val) + ".reti"), instrs_block_free
                )
            case _:
                bug_in_compiler(file)
