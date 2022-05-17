from picoc_nodes import N as PN
from reti_nodes import N as RN
from errors import Errors
from symbol_table import SymbolTable, Symbol
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
        self.symbol_table = SymbolTable()

    def _bug_in_compiler_error(self, *args):
        import inspect

        # return name of caller of this function
        raise Errors.BugInCompiler(inspect.stack()[1][3], args_to_str(args))

    # =========================================================================
    # =                           PicoC -> PicoC_mon                          =
    # =========================================================================

    def _picoc_to_picoc_mon_exp(self, exp):
        match exp:
            case PN.Name():
                pass
            case PN.Num():
                pass
            case PN.Char():
                pass
            case PN.BinOp(left_exp, bin_op, right_exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_to_picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        PN.Exp(
                            PN.BinOp(
                                PN.Stack(PN.Num("1")), bin_op, PN.Stack(PN.Num("2"))
                            )
                        )
                    ]
                )
            case PN.UnOp(un_op, exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.UnOp(un_op, PN.Stack(PN.Num("1"))))]
            case PN.Atom(left_exp, relation, right_exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(left_exp)
                exps2_mon = self._picoc_to_picoc_mon_exp(right_exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [
                        PN.Exp(
                            PN.Atom(
                                PN.Stack(PN.Num("1")), relation, PN.Stack(PN.Num("2"))
                            )
                        )
                    ]
                )
            case PN.ToBool(exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Exp(PN.Stack(PN.Num("1")))]
            case PN.Deref(deref_loc, exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(deref_loc)
                exps2_mon = self._picoc_to_picoc_mon_exp(exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [PN.Deref(PN.Stack(PN.Num("1")), PN.Stack(PN.Num("2")))]
                )
            case PN.Ref(ref_loc):
                exps_mon = self._picoc_to_picoc_mon_exp(ref_loc)
                return exps_mon + [PN.Ref(PN.Stack(PN.Num("1")))]
            case PN.Subscr(deref_loc, exp):
                exps1_mon = self._picoc_to_picoc_mon_exp(deref_loc)
                exps2_mon = self._picoc_to_picoc_mon_exp(exp)
                return (
                    exps1_mon
                    + exps2_mon
                    + [PN.Subscr(PN.Stack(PN.Num("1")), PN.Stack(PN.Num("2")))]
                )
            case PN.Attr(ref_loc, name):
                exps_mon = self._picoc_to_picoc_mon_exp(ref_loc)
                return exps_mon + [PN.Attr(PN.Stack(PN.Num("1")), name)]
            case PN.Call(name, exps):
                exps_mon = []
                for exp in exps:
                    exps_mon += self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Call(name, PN.Stack(PN.Num("1")))]
            case _:
                return [exp]

    def _picoc_to_picoc_mon_stmt(self, stmt):
        match stmt:
            case PN.Assign(assign_lhs, exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Assign(assign_lhs, PN.Stack(PN.Num("1")))]
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
            case PN.Assign(PN.Alloc(type_qual, datatype, name), PN.Array(exps)):
                exps_mon = []
                stack_locs = []
                for i, exp in enumerate(exps):
                    exps_mon = self._picoc_to_picoc_mon_stmt(exp)
                    stack_locs += [PN.Stack(PN.Num(str(i + 1)))]
                return exps_mon + [
                    PN.Assign(PN.Alloc(type_qual, datatype, name), PN.Array(stack_locs))
                ]
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
            case PN.Exp(alloc_call):
                exps_mon = self._picoc_to_picoc_mon_exp(alloc_call)
                return exps_mon + [PN.Exp(PN.Stack(PN.Num("1")))]
            case PN.Return(exp):
                exps_mon = self._picoc_to_picoc_mon_exp(exp)
                return exps_mon + [PN.Return(PN.Stack(PN.Num("1")))]
            case _:
                self._bug_in_compiler_error(stmt)

    def _picoc_to_picoc_mon_def(self, decl_def):
        match decl_def:
            case PN.FunDef(datatype, name, params, stmts):
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return PN.FunDef(datatype, name, params, stmts_mon)
            case _:
                return decl_def

    def picoc_to_picoc_mon(self, file: PN.File):
        match file:
            case PN.File(name, decls_defs):
                decls_defs_mon = []
                for decl_def in decls_defs:
                    decls_defs_mon += [self._picoc_to_picoc_mon_def(decl_def)]
        return PN.File(name, decls_defs_mon)

    # =========================================================================
    # =                       PicoC_mon -> PicoC_Blocks                       =
    # =========================================================================

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = PN.Block(PN.Name(label), stmts)
        blocks[label] = new_block
        self.block_id += 1
        return PN.GoTo(PN.Name(label))

    def _picoc_mon_to_picoc_blocks_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
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
            case PN.While(exp, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                goto_condition_check = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_blocks_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.name.value = self._create_block(
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
                goto_branch.name.value = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).name.value

                return [goto_branch]
            case PN.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_mon_to_picoc_blocks_def(self, decl_def):
        match decl_def:
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
            case PN.File(name, decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += [self._picoc_mon_to_picoc_blocks_def(decl_def)]
        return PN.File(name, decls_defs_blocks)

    # =========================================================================
    # =                      PicoC_Blocks -> RETI_Blocks                      =
    # =========================================================================
    def _picoc_blocks_to_reti_blocks_loc(self, loc):
        match loc:
            case PN.Name(val):
                return [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Num("1")]),
                    RN.Instr(RN.Load(), [RN.Reg(RN.Acc()), RN.Num(val)]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Num("1")]
                    ),
                ]
            case PN.Num(val):
                return [
                    RN.Instr(RN.Subi(), [RN.Reg(RN.Sp()), RN.Num("1")]),
                    RN.Instr(RN.Loadi(), [RN.Reg(RN.Acc()), RN.Num(val)]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Num("1")]
                    ),
                ]
            case _:
                self._bug_in_compiler_error(loc)

    def _picoc_blocks_to_reti_blocks_exp(self, exp):
        match exp:
            case PN.BinOp(PN.Stack(num1), bin_op, PN.Stack(num2)):
                reti_instrs = []
                match bin_op:
                    case PN.Add():
                        op = RN.Add()
                    case PN.Sub():
                        op = RN.Sub()
                    case PN.Mul():
                        op = RN.Mult()
                    case PN.Div():
                        op = RN.Div()
                    case PN.Mod():
                        op = RN.Mod()
                    case PN.Oplus():
                        op = RN.Oplus()
                    case PN.And():
                        op = RN.And()
                    case PN.Or():
                        op = RN.Or()
                    case _:
                        self._bug_in_compiler_error(exp)
                return reti_instrs + [
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Num("2")]
                    ),
                    RN.Instr(
                        RN.Loadin(), [RN.Reg(RN.Sp()), RN.Reg(RN.In2()), RN.Num("1")]
                    ),
                    RN.Instr(op, [RN.Reg(RN.Acc()), RN.Reg(RN.In2())]),
                    RN.Instr(
                        RN.Storein(), [RN.Reg(RN.Sp()), RN.Reg(RN.Acc()), RN.Num("2")]
                    ),
                    RN.Instr(RN.Addi(), [RN.Reg(RN.Sp()), RN.Num("1")]),
                ]
            case PN.Alloc(type_qual, datatype, pntr_decl):
                match pntr_decl:
                    case PN.PntrDecl(PN.Num(), PN.ArrayDecl(PN.Name(name, pos), [])):
                        symbol = Symbol(type_qual, datatype, name, "-", pos)
                        self.symbol_table.define(symbol)
                        return []
                    case _:
                        self._bug_in_compiler_error(exp)
            case _:
                self._bug_in_compiler_error(exp)

    def _picoc_blocks_to_reti_blocks_stmt(self, stmt):
        match stmt:
            case PN.Exp(PN.Call(PN.Name("print"), exp)):
                pass
            case PN.Exp(alloc):
                return self._picoc_blocks_to_reti_blocks_exp(alloc)
            case PN.Assign(assign_lhs, exp):
                reti_instrs = []
                self._picoc_blocks_to_reti_blocks_loc(assign_lhs)
                reti_instrs += self._picoc_blocks_to_reti_blocks_exp(exp)
                match assign_lhs:
                    # TODO: der zweite Case muss nach Visitor verändert werden
                    case (
                        PN.Name(name, pos)
                        | PN.Alloc(
                            _, _, PN.PntrDecl(_, PN.ArrayDecl(PN.Name(name, pos), _))
                        )
                    ):
                        symbol = self.symbol_table.resolve(name)
                        match symbol:
                            case Symbol("writable", "int", _, val, _):
                                return reti_instrs + [
                                    RN.Instr(
                                        RN.Loadin(), [RN.Sp(), RN.Acc(), RN.Num("1")]
                                    ),
                                    RN.Instr(RN.Addi(), [RN.Sp(), RN.Num(1)]),
                                    RN.Instr(RN.Store(), [RN.Acc(), RN.Num(val)]),
                                ]
                            case Symbol("writable", "char", _, val, _):
                                # TODO: implicit cast code
                                return reti_instrs + [
                                    RN.Instr(
                                        RN.Loadin(), [RN.Sp(), RN.Acc(), RN.Num("1")]
                                    ),
                                    RN.Instr(RN.Addi(), [RN.Sp(), RN.Num(1)]),
                                    RN.Instr(RN.Store(), [RN.Acc(), RN.Num(val)]),
                                ]
                            case Symbol("const", _, _, _, pos2):
                                # TODO: ConstReassignment schreiben
                                raise Errors.ConstReassignment(name, pos, pos2)
                            case _:
                                self._bug_in_compiler_error(exp)
                    case _:
                        self._bug_in_compiler_error(exp)
            case PN.Assign(PN.Alloc(type_qual, datatype, pntr_decl), PN.Array(exps)):
                pass
            case PN.Assign(
                PN.Alloc(type_qual, datatype, pntr_decl), PN.Struct(assigns)
            ):
                pass
            case PN.Assign(PN.Alloc(type_qual, datatype, pntr_decl), exp):
                pass
            case PN.If(exp, stmts):
                pass
            case PN.IfElse(exp, stmts1, stmts2):
                pass
            case PN.While(exp, stmts):
                pass
            case PN.DoWhile(exp, stmts):
                pass
            case PN.Exp(PN.Call(identifier, exps)):
                pass
            case PN.Return(exp):
                pass
            case PN.GoTo(name):
                pass
            case _:
                self._bug_in_compiler_error()

    def _picoc_blocks_to_reti_blocks_def(self, decl_def):
        match decl_def:
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
