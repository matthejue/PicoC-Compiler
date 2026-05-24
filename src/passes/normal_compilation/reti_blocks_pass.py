from src.passes.dependencies import *


class RetiBlocksPass:
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
            case pn.Exp(pn.FunRef(pn.Name(fun_name))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Name(fun_name)]),
                    rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
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
            case pn.Assign(rn.Reg() as reg, pn.Stack(pn.Num(val))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(),
                        [rn.Reg(rn.Sp()), reg, rn.Im(val)],
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
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
                    case (
                        pn.StructSpec()
                        | pn.PntrDecl()
                        | pn.FunPtrDecl()
                        | pn.IntType()
                        | pn.CharType()
                    ):
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
            case pn.Exp(pn.GoTo(rn.Reg() as reg)):
                instr = rn.Instr(rn.Move(), [reg, rn.Reg(rn.Pc())])
                instr.call_target_function = getattr(stmt, "call_target_function", None)
                instr.indirect_call = getattr(stmt, "indirect_call", False)
                return self._single_line_comment(stmt, "#") + [
                    instr
                ]
            case pn.Exp(pn.GoTo(pn.Stack(pn.Num(val)))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(),
                        [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im(val)],
                    )
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
                return_offset = (
                    int(stmt.return_offset.val)
                    if not isinstance(stmt.return_offset, pn.Empty)
                    else 4 + (3 if global_vars.args.no_long_jumps else 0)
                )
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
                                return_offset,
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
                return_instr = rn.Instr(
                    rn.Loadin(),
                    [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")],
                )
                return_instr.return_statement = True
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                    return_instr,
                ]
            case pn.Return(pn.Empty()):
                # TODO(frame-layout): update return-address access for the new
                # frame layout.
                return_instr = rn.Instr(
                    rn.Loadin(),
                    [rn.Reg(rn.Baf()), rn.Reg(rn.Pc()), rn.Im("-1")],
                )
                return_instr.return_statement = True
                return self._single_line_comment(stmt, "#") + [return_instr]
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
                                instrs += self._inherit_origin_many(
                                    self._reti_blocks_stmt(stmt), stmt
                                )
                            block.stmts_instrs[:] = instrs
                        case _:
                            throw_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_blocks"),
                    [pn.Section(".text", blocks)],
                )
            case _:
                throw_error(file)
