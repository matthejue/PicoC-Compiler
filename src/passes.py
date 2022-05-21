from picoc_nodes import N as PN
from reti_nodes import N as RN
from errors import Errors
from symbol_table import ST
from error_handler import args_to_str


class Passes:
    def __init__(self):
        # PicoC_mon -> PicoC_Blocks
        self.block_id = 0
        self.all_blocks = dict()
        # PicoC_Blocks -> RETI_Blocks
        self.instrs_cnt = 0
        self.current_scope = "global"
        self.current_address = 0
        self.symbol_table = ST.SymbolTable()

    def _bug_in_compiler_error(self, *args):
        import inspect

        # return name of caller of this function
        raise Errors.BugInCompiler(inspect.stack()[1][3], args_to_str(args))

    # =========================================================================
    # =                         PicoC -> PicoC_Shrink                         =
    # =========================================================================
    # =========================================================================
    # =                       PicoC_Shrink -> PicoC_Mon                       =
    # =========================================================================
    # =========================================================================
    # =                           PicoC -> PicoC_Mon                          =
    # =========================================================================

    def _picoc_to_picoc_mon_ref(self, ref_loc, prev_refs):
        match ref_loc:
            # ---------------------------- L_Arith ----------------------------
            case PN.Name(val):
                symbol = self.symbol_table.resolve(val)
                match symbol:
                    case ST.Symbol(_, datatype):
                        current_datatype = datatype
                    case _:
                        self._bug_in_compiler_error()
                while prev_refs:
                    match current_datatype:
                        case (PN.CharType() | PN.IntType()):
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            break
                        case PN.PntrDecl(PN.Num(val), datatype):
                            if int(val) == 0:
                                current_datatype = datatype
                            current_datatype.num.val = int(val) - 1
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                        case PN.ArrayDecl(nums, datatype):
                            if len(nums) == 0:
                                current_datatype = datatype
                            current_datatype.nums = nums[1:]
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                        case PN.StructSpec(PN.Name(val)):
                            ref = prev_refs.pop()
                            ref.datatype = current_datatype
                            match ref:
                                case PN.Ref(PN.Attr(ref_loc, PN.Name(val2))):
                                    symbol = self.symbol_table.resolve(f"{val2}@{val}")
                                case _:
                                    # TODO: here belongs a proper error message
                                    # nachsehen, ob [] auf Structvariable anwendbar ist
                                    self._bug_in_compiler_error()
                            match symbol:
                                case ST.Symbol(_, datatype):
                                    current_datatype = datatype
                                case _:
                                    self._bug_in_compiler_error()
                        case _:
                            self._bug_in_compiler_error()
            # --------------------------- L_Pointer ---------------------------
            # TODO: remove after implementing shrink pass
            case PN.Deref(deref_loc, exp):
                ref = PN.Ref(ref_loc)
                refs_mon = self._picoc_to_picoc_mon_ref(deref_loc, [ref] + prev_refs)
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return refs_mon + exps_mon + [PN.Exp(ref)]
            # ---------------------------- L_Array ----------------------------
            case PN.Subscr(deref_loc, exp):
                ref = PN.Ref(ref_loc)
                refs_mon = self._picoc_to_picoc_mon_ref(deref_loc, [ref] + prev_refs)
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return refs_mon + exps_mon + [PN.Exp(ref)]
            # ---------------------------- L_Struct ---------------------------
            case PN.Attr(ref_loc2, _):
                ref = PN.Ref(ref_loc)
                refs_mon = self._picoc_to_picoc_mon_ref(ref_loc2, [ref] + prev_refs)
                return refs_mon + [PN.Exp(ref)]
            case _:
                self._bug_in_compiler_error(ref_loc)

    def _picoc_to_picoc_mon_exp(self, exp):
        match exp:
            # ---------------------------- L_Arith ----------------------------
            case (PN.Name() | PN.Num() | PN.Char()):
                return [PN.Exp(exp)]
            # ----------------------- L_Arith + L_Logic -----------------------
            case PN.BinOp(left_exp, bin_op, right_exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_to_picoc_mon_exp(right_exp)
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
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.UnOp(un_op, PN.Stack(PN.Num("1"))))]
            # ---------------------------- L_Logic ----------------------------
            case PN.Atom(left_exp, relation, right_exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_to_picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        PN.Exp(
                            PN.Atom(
                                PN.Stack(PN.Num("2")), relation, PN.Stack(PN.Num("1"))
                            )
                        )
                    ]
                )
            case PN.ToBool(exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.ToBool(PN.Stack(PN.Num("1"))))]
            # ------------------------- L_Assign_Alloc ------------------------
            case PN.Alloc():
                return [PN.Exp(exp)]
            # --------------------------- L_Pointer ---------------------------
            # TODO
            case PN.Deref(deref_loc, exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(deref_loc)
                exps2_mon = self._picoc_to_picoc_mon_exp(exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [PN.Exp(PN.Deref(PN.Stack(PN.Num("2")), PN.Stack(PN.Num("1"))))]
                )
            case PN.Ref(PN.Name() as ref_loc):
                return [PN.Exp(PN.Ref(ref_loc))]
            case PN.Ref(
                (PN.Deref(deref_loc, exp) | PN.Subscr(deref_loc, exp) as ref_loc)
            ):
                refs_mon = self._picoc_to_picoc_mon_ref(deref_loc, [])
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return refs_mon + exps_mon + [PN.Exp(PN.Ref(ref_loc))]
            case PN.Ref(PN.Attr(ref_loc, name) as ref_loc2):
                refs_mon = self._picoc_to_picoc_mon_ref(ref_loc, [])
                return refs_mon + [PN.Exp(PN.Ref(ref_loc2))]
            # ---------------------------- L_Array ----------------------------
            case PN.Subscr(deref_loc, exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(deref_loc)
                exps2_mon = self._picoc_to_picoc_mon_exp(exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [PN.Exp(PN.Subscr(PN.Stack(PN.Num("2")), PN.Stack(PN.Num("1"))))]
                )
            # ---------------------------- L_Struct ---------------------------
            case PN.Attr(ref_loc, name):
                exps_mon = self._picoc_to_picoc_mon_exp(ref_loc)
                return exps_mon + [PN.Exp(PN.Attr(PN.Stack(PN.Num("1")), name))]
            # ----------------------------- L_Fun -----------------------------
            case PN.Call(name, exps):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon += self._picoc_to_picoc_mon_exp(exp)
                    stack_locs += [PN.Stack(PN.Num(str(i + 1)))]
                return exps_mon + [PN.Exp(PN.Call(name, stack_locs))]
            case _:
                self._bug_in_compiler_error(exp)

    def _picoc_to_picoc_mon_stmt(self, stmt):
        match stmt:
            # ------------------------- L_Assign_Alloc ------------------------
            case PN.Assign(PN.Alloc(type_qual, datatype, name) as alloc, exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(exp)
                exps2_mon = self._picoc_to_picoc_mon_exp(alloc)
                return exps1_mon + exps2_mon + [PN.Assign(name, PN.Stack(PN.Num("1")))]
            case PN.Assign(ref_loc, exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Assign(ref_loc, PN.Stack(PN.Num("1")))]
            # --------------------- L_Assign_Alloc + L_Fun --------------------
            case PN.Exp(alloc_call):
                exps_mon = self._picoc_to_picoc_mon_exp(alloc_call)
                return exps_mon
            # ---------------------------- L_Array ----------------------------
            case PN.Assign(PN.Alloc(type_qual, datatype, name), PN.Array(exps)):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon = self._picoc_to_picoc_mon_stmt(exp)
                    stack_locs += [PN.Stack(PN.Num(str(i + 1)))]
                return exps_mon + [
                    PN.Assign(PN.Alloc(type_qual, datatype, name), PN.Array(stack_locs))
                ]
            # ---------------------------- L_Struct ---------------------------
            case PN.Assign(PN.Alloc(type_qual, datatype, name), PN.Struct(assigns)):
                exps_mon = []
                assigns_mon = []
                for i, assign in enumerate(assigns):
                    match assign:
                        case PN.Assign(assign_lhs, exp):
                            exps_mon += self._picoc_to_picoc_mon_exp(exp)
                            assigns_mon += [
                                PN.Assign(assign_lhs, PN.Stack(PN.Num(i + 1)))
                            ]
                return exps_mon + [
                    PN.Assign(
                        PN.Alloc(type_qual, datatype, name),
                        PN.Struct(assigns_mon),
                    )
                ]
            # --------------------------- L_If_Else ---------------------------
            case PN.If(exp, stmts):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return exps_mon + [PN.If(PN.Stack(PN.Num("1")), stmts_mon)]
            case PN.IfElse(exp, stmts1, stmts2):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                stmts1_mon = []
                for stmt1 in stmts1:
                    stmts1_mon += self._picoc_to_picoc_mon_stmt(stmt1)
                stmts2_mon = []
                for stmt2 in stmts2:
                    stmts2_mon += self._picoc_to_picoc_mon_stmt(stmt2)
                return exps_mon + [
                    PN.IfElse(PN.Stack(PN.Num("1")), stmts1_mon, stmts2_mon)
                ]
            # ----------------------------- L_Loop ----------------------------
            case PN.While(exp, stmts):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return exps_mon + [PN.While(PN.Stack(PN.Num("1")), stmts_mon)]
            case PN.DoWhile(exp, stmts):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return exps_mon + [PN.DoWhile(PN.Stack(PN.Num("1")), stmts_mon)]
            # ----------------------------- L_Fun -----------------------------
            case PN.Return(exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Return(PN.Stack(PN.Num("1")))]
            case _:
                self._bug_in_compiler_error(stmt)

    def _picoc_to_picoc_mon_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case PN.FunDef(datatype, name, params, stmts):
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return PN.FunDef(datatype, name, params, stmts_mon)
            case _:
                return decl_def

    def picoc_to_picoc_mon(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(name, decls_defs):
                decls_defs_mon = []
                for decl_def in decls_defs:
                    decls_defs_mon += [self._picoc_to_picoc_mon_def(decl_def)]
        return PN.File(name, decls_defs_mon)

    # =========================================================================
    # =                       PicoC_Mon -> PicoC_Blocks                       =
    # =========================================================================

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = PN.Block(PN.Name(label), stmts)
        blocks[label] = new_block
        self.block_id += 1
        return PN.GoTo(PN.Name(label))

    def _picoc_mon_to_picoc_blocks_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            # --------------------------- L_If_Else ---------------------------
            case PN.If(exp, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_if = [goto_after]
                for stmt in reversed(stmts):
                    stmts_if = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.If(exp, [goto_if])]
            case PN.IfElse(exp, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_else, blocks
                    )
                goto_else = self._create_block("else", stmts_else, blocks)

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.IfElse(exp, [goto_if], [goto_else])]
            # ----------------------------- L_Loop ----------------------------
            case PN.While(exp, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                goto_condition_check = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.name.val = self._create_block(
                    "while_branch", stmts_while, blocks
                ).name.val

                condition_check = [PN.IfElse(exp, goto_branch, goto_after)]
                goto_condition_check.name.val = self._create_block(
                    "condition_check", condition_check, blocks
                ).name.val

                return [goto_condition_check]
            case PN.DoWhile(exp, stmts):
                goto_after = self._create_block(
                    "do_while_after", processed_stmts, blocks
                )

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [PN.IfElse(exp, goto_branch, goto_after)]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.name.val = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).name.val

                return [goto_branch]
            # ----------------------------- L_Fun -----------------------------
            case PN.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_mon_to_picoc_blocks_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case PN.FunDef(datatype, PN.Name(fun_name) as name, params, stmts):
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, processed_stmts, blocks
                    )
                self._create_block(fun_name, processed_stmts, blocks)
                self.all_blocks |= blocks
                return PN.FunDef(
                    datatype,
                    name,
                    params,
                    list(
                        sorted(
                            blocks.values(),
                            key=lambda block: -int(
                                block.name.val[block.name.val.rindex(".") + 1 :]
                            ),
                        )
                    ),
                )
            case _:
                return decl_def

    def picoc_mon_to_picoc_blocks(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(name, decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += [self._picoc_mon_to_picoc_blocks_def(decl_def)]
        return PN.File(name, decls_defs_blocks)

    # =========================================================================
    # =                      PicoC_Blocks -> RETI_Blocks                      =
    # =========================================================================

    def _picoc_blocks_to_reti_blocks_stmt(self, stmt):
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
                    case PN.LogicAnd:
                        lop = RN.And()
                    case PN.LogicOr:
                        lop = RN.Or()
                    case _:
                        self._bug_in_compiler_error(bin_lop)
                return [
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
            case PN.UnOp(PN.LogicNot, PN.Stack(PN.Num(val))):
                return [
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
                reti_instrs = [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                ]
                try:
                    symbol = self.symbol_table.resolve(val)
                except KeyError:
                    raise Errors.UnknownIdentifier(val, pos)
                match symbol:
                    # TODO: anpassen an Nutzung von DS um nur Relativadressen zu nutzen
                    case ST.Symbol(PN.Writeable(), _, _, PN.Num(val)):
                        reti_instrs += [
                            RN.Instr(RN.Load(), [RN.Reg(RN.Acc()), RN.Im(val)]),
                        ]
                    case ST.Symbol(PN.Const(), _, _, PN.Num(val)):
                        reti_instrs += [
                            RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Im(val)]),
                        ]
                    case _:
                        self._bug_in_compiler_error(symbol)

                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    ),
                ]
            case (PN.Exp(PN.Num(val) as datatype) | PN.Exp(PN.Char(val) as datatype)):
                reti_instrs = [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
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
                        self._bug_in_compiler_error(bin_aop)
                return [
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
            case PN.UnOp(un_op, PN.Stack(PN.Num(val))):
                reti_instrs = [
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
                        self._bug_in_compiler_error(un_op)
                return reti_instrs + [
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im("1")]
                    )
                ]
            case PN.Exp(PN.Call(PN.Name("input"), [PN.Stack(PN.Num(val))])):
                return [
                    RN.Call(RN.Name("input"), RN.Reg(RN.Acc())),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val)]
                    ),
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                ]
            case PN.Exp(PN.Call(PN.Name("print"), [PN.Stack(PN.Num(val))])):
                return [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val)]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                    RN.Call(RN.Name("print"), RN.Reg(RN.Acc())),
                ]
            # ---------------------------- L_Logic ----------------------------
            case PN.Exp(PN.ToBool(PN.Stack(val))):
                return [
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
                    case PN.Eq:
                        rel = RN.Eq()
                    case PN.NEq:
                        rel = RN.NEq()
                    case PN.Lt:
                        rel = RN.Lt()
                    case PN.LtE:
                        rel = RN.LtE()
                    case PN.Gt:
                        rel = RN.Gt()
                    case PN.GtE:
                        rel = RN.GtE()
                    case _:
                        self._bug_in_compiler_error(rel)
                return [
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
            case PN.Exp(PN.Alloc(type_qual, datatype, name)):
                match name:
                    case PN.Name(val, pos):
                        symbol = ST.Symbol(
                            type_qual,
                            datatype,
                            name,
                            ST.Empty(),
                            ST.Pos(PN.Num(pos.line), PN.Num(pos.column)),
                        )
                        self.symbol_table.define(symbol)
                return []
            case PN.Assign(PN.Name(val), PN.Stack(PN.Num(val2))):
                symbol = self.symbol_table.resolve(val)
                match symbol:
                    case ST.Symbol(_, _, _, PN.Num(val1)):
                        return [
                            RN.Instr(
                                RN.Loadin(),
                                [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Im(val2)],
                            ),
                            RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Im("1")]),
                            RN.Instr(
                                RN.Store(),
                                [RN.Reg(RN.Acc()), RN.Im(val1)],
                            ),
                        ]
                    case _:
                        self._bug_in_compiler_error()
            case PN.Assign(PN.Stack(PN.Num(val1)), PN.Stack(PN.Num(val2))):
                return [
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
            #  # --------------------------- L_Pointer ---------------------------
            #  # ---------------------------- L_Array ----------------------------
            #  case PN.Assign(PN.Alloc(type_qual, datatype, pntr_decl), PN.Array(exps)):
            #      pass
            #  # ---------------------------- L_Struct ---------------------------
            #  case PN.Assign(
            #      PN.Alloc(type_qual, datatype, pntr_decl), PN.Struct(assigns)
            #  ):
            #      pass
            #  case PN.Assign(PN.Alloc(type_qual, datatype, pntr_decl), exp):
            #      pass
            #  # --------------------------- L_If_Else ---------------------------
            #  case PN.If(exp, stmts):
            #      pass
            #  case PN.IfElse(exp, stmts1, stmts2):
            #      pass
            #  # ----------------------------- L_Loop ----------------------------
            #  case PN.While(exp, stmts):
            #      pass
            #  case PN.DoWhile(exp, stmts):
            #      pass
            #  # ----------------------------- L_Fun -----------------------------
            #  case PN.Exp(PN.Call(identifier, exps)):
            #      pass
            #  case PN.Return(exp):
            #      pass
            #  case PN.GoTo(name):
            #      pass
            case _:
                self._bug_in_compiler_error(stmt)

    def _picoc_blocks_to_reti_blocks_def(self, decl_def):
        match decl_def:
            # ------------------------ L_Fun + L_Blocks -----------------------
            case PN.FunDef(_, PN.Name(identifier), _, blocks):
                self.current_scope = identifier
                self.current_address = 0
                for block in blocks:
                    match block:
                        case PN.Block(_, stmts):
                            reti_instrs = []
                            for stmt in stmts:
                                reti_instrs += self._picoc_blocks_to_reti_blocks_stmt(
                                    stmt
                                )
                            block.stmts_instrs = reti_instrs
                            block.instrs_after = (
                                f"instructions after: {self.instrs_cnt}"
                            )
                            self.instrs_cnt += len(reti_instrs)
                return blocks
            case PN.FunDecl():
                return []
            case PN.StructDecl():
                return []
            case _:
                self._bug_in_compiler_error()

    def picoc_blocks_to_reti_blocks(self, file: PN.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case PN.File(name, decls_defs):
                reti_blocks = []
                for decl_def in decls_defs:
                    reti_blocks += self._picoc_blocks_to_reti_blocks_def(decl_def)
        return RN.Program(name, reti_blocks)

    # =========================================================================
    # =                          RETI_Blocks -> RETI                          =
    # =========================================================================

    def reti_block_to_reti(self):
        ...
