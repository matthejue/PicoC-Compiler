from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.ast_transformers import TransformerRetiBlocks
from src.passes.compilation import opt_level_1
from src.utils.util_funs_dependent import throw_error
import copy


class RetiBlocksPass:
    def _parse_asm(self, code):
        if not code.strip():
            return []
        transformer = TransformerRetiBlocks()
        asm_code = "_asm:\n" + code.strip() + "\n"
        tree = transformer.parse_tree(asm_code)
        if tree.root_node.has_error:
            throw_error(f"Invalid RETI asm: {code}")
        file = transformer.build_ast(tree, asm_code)

        match file:
            case pn.File(_, [pn.Block("_asm", instrs)]):
                return instrs
            case _:
                throw_error(f"Unsupported asm block: {code}")

    def _global_base_reg(self, symbol_name):
        symbol, _ = self.symbol_table.resolve(symbol_name, scope="global")
        if isinstance(symbol, dict) and symbol.get("section") == "interrupt_vector_table":
            return rn.Reg(rn.Cs())
        return rn.Reg(rn.Ds())

    def _stackframe_access_offset(self, loc, tmp_idx=0):
        tmp_idx = int(tmp_idx)
        match loc:
            case pn.StackframeParam(pn.Num(addr)):
                addr = int(addr)
                return 3 + addr + tmp_idx
            case pn.StackframeLocalVar(pn.Num(addr)):
                addr = int(addr)
                return -(addr - tmp_idx)
            case _:
                throw_error(loc)

    def _add_signed_offset(self, reg, offset):
        offset = int(offset)
        op = rn.Addi() if offset >= 0 else rn.Subi()
        return rn.Instr(op, [reg, rn.Im(str(abs(offset)))])

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
                reti_instrs = self._single_line_comment(stmt, "#")
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
                            rn.Instr(rn.Push(), [exp]),
                        ]
                    case _:
                        throw_error(exp)

                return reti_instrs + [
                    rn.Instr(rn.Push(), [rn.Reg(rn.Acc())]),
                ]
            case pn.Exp(pn.FunRef(pn.Name(fun_name))):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Loadi32(), [rn.Reg(rn.Acc()), rn.Name(fun_name)]),
                    rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                    rn.Instr(rn.Push(), [rn.Reg(rn.Acc())]),
                ]
            case pn.Exp((pn.Global() | pn.StackframeLocalVar() | pn.StackframeParam()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#")
                match exp:
                    case pn.Global(pn.Name(val2)):
                        name = rn.Name(val2)
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [self._global_base_reg(val2), rn.Reg(rn.Acc()), name],
                            ),
                        ]
                    case pn.StackframeLocalVar() | pn.StackframeParam():
                        reti_instrs += [
                            rn.Instr(
                                rn.Loadin(),
                                [
                                    rn.Reg(rn.Baf()),
                                    rn.Reg(rn.Acc()),
                                    rn.Im(
                                        str(
                                            self._stackframe_access_offset(
                                                exp
                                            )
                                        )
                                    ),
                                ],
                            ),
                        ]
                return reti_instrs + [rn.Instr(rn.Push(), [rn.Reg(rn.Acc())])]
            case pn.Ref((pn.Global() | pn.StackframeLocalVar() | pn.StackframeParam()) as exp):
                reti_instrs = self._single_line_comment(stmt, "#")
                match exp:
                    case pn.Global(pn.Name(val)):
                        name = rn.Name(val)
                        reti_instrs += [
                            rn.Instr(rn.Loadi32(), [rn.Reg(rn.In1()), name]),
                            rn.Instr(rn.Add(), [rn.Reg(rn.In1()), self._global_base_reg(val)]),
                        ]
                    case pn.StackframeLocalVar() | pn.StackframeParam():
                        offset = self._stackframe_access_offset(exp)
                        reti_instrs += [
                            rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.In1())]),
                            self._add_signed_offset(rn.Reg(rn.In1()), offset),
                        ]
                    case _:
                        throw_error(exp)
                return reti_instrs + [
                    rn.Instr(rn.Push(), [rn.Reg(rn.In1())])
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
            case pn.Exp(pn.Asm(pn.String(code))):
                return self._single_line_comment(stmt, "#") + self._parse_asm(code)
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
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.Acc()), rn.Im(val)]),
                    rn.Instr(rn.Push(), [rn.Reg(rn.Acc())]),
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
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.In1()), rn.Im("1")]),
                    rn.Jump(rel, rn.Im("2")),
                    rn.Instr(rn.Loadi(), [rn.Reg(rn.In1()), rn.Im("0")]),
                    rn.Instr(
                        rn.Storein(), [rn.Reg(rn.Sp()), rn.Reg(rn.In1()), rn.Im("2")]
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
            # ------------------------- L_Assign_Alloc ------------------------
            case pn.Assign(rn.Reg() as reg, pn.Stack(pn.Num(val))):
                if str(val) == "1":
                    return self._single_line_comment(stmt, "#") + [
                        rn.Instr(rn.Pop(), [reg]),
                    ]
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadin(),
                        [rn.Reg(rn.Sp()), reg, rn.Im(val)],
                    ),
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                ]
            case pn.Assign(
                pn.Stack(pn.Num(val1)) as lhs,
                (pn.Global() | pn.StackframeLocalVar() | pn.StackframeParam()) as exp,
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
                            constant = int(val1)
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        self._global_base_reg(val2),
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
                                        rn.Im(str(constant + 1)),
                                    ],
                                ),
                            ]
                        case (pn.Stack(pn.Num(val1)), pn.StackframeLocalVar() | pn.StackframeParam()):
                            reti_instrs += [
                                rn.Instr(
                                    rn.Loadin(),
                                    [
                                        rn.Reg(rn.Baf()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(
                                            str(
                                                self._stackframe_access_offset(
                                                    mem, val1
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
                (pn.Global() | pn.StackframeLocalVar() | pn.StackframeParam()) as lhs,
                pn.Stack(pn.Num(val2)) as tmp,
            ):
                tmp_max = tmp.num.val
                mem = copy.deepcopy(lhs)
                tmp = pn.Stack(pn.Num(0))
                reti_instrs = []
                stack_offset = val2
                reti_instrs = self._single_line_comment(stmt, "#")
                if int(tmp_max) == 1 and int(stack_offset) == 1:
                    match mem:
                        case pn.Global(pn.Name(val1)):
                            return reti_instrs + [
                                rn.Instr(rn.Pop(), [rn.Reg(rn.Acc())]),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        self._global_base_reg(val1),
                                        rn.Reg(rn.Acc()),
                                        rn.Name(val1),
                                    ],
                                ),
                            ]
                        case pn.StackframeLocalVar() | pn.StackframeParam():
                            return reti_instrs + [
                                rn.Instr(rn.Pop(), [rn.Reg(rn.Acc())]),
                                rn.Instr(
                                    rn.Storein(),
                                    [
                                        rn.Reg(rn.Baf()),
                                        rn.Reg(rn.Acc()),
                                        rn.Im(
                                            str(
                                                self._stackframe_access_offset(
                                                    mem, 0
                                                )
                                            )
                                        ),
                                    ],
                                ),
                            ]
                        case _:
                            throw_error(mem)
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
                                        self._global_base_reg(val1),
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
                        case (pn.StackframeLocalVar() | pn.StackframeParam(), pn.Stack(pn.Num(val2))):
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
                                                    mem,
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
            case pn.IfElse(
                pn.Stack(pn.Num(val)),
                [pn.GoTo(pn.Name()) as goto1],
                [pn.GoTo(pn.Name(goto2_name))],
            ):
                if str(val) == "1":
                    condition_instrs = [
                        rn.Instr(rn.Pop(), [rn.Reg(rn.Acc())]),
                        rn.Jump32(rn.Eq(), rn.Name(goto2_name)),
                    ]
                else:
                    condition_instrs = [
                        rn.Instr(
                            rn.Loadin(), [rn.Reg(rn.Sp()), rn.Reg(rn.Acc()), rn.Im(val)]
                        ),
                        rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im("1")]),
                        rn.Jump32(rn.Eq(), rn.Name(goto2_name)),
                    ]
                return (
                    self._single_line_comment(stmt, "#")
                    + condition_instrs
                    + self._single_line_comment(goto1, "#")
                    + self._reti_blocks_stmt(pn.Exp(goto1))
                )
            case pn.Exp(pn.GoTo(pn.Name(val))):
                block_name = val
                return self._single_line_comment(stmt, "#") + [
                    rn.Jump32(rn.Always(), rn.Name(block_name))
                ]
            case pn.Exp(pn.GoTo(rn.Reg() as reg)):
                instr = rn.Instr(rn.Move(), [reg, rn.Reg(rn.Pc())])
                return self._single_line_comment(stmt, "#") + [
                    instr
                ]
            case pn.Exp(pn.GoTo(pn.Stack(pn.Num(val)))):
                if str(val) != "1":
                    throw_error(
                        f"Function call GoTo(Stack(...)) must use Stack(1), got Stack({val})"
                    )
                instr = rn.Instr(rn.Move(), [rn.Reg(rn.Acc()), rn.Reg(rn.Pc())])
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Pop(), [rn.Reg(rn.Acc())]),
                    instr,
                ]
            # ----------------------------- L_Fun -----------------------------
            case pn.SaveReturnAddress(pn.Name(label)):
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(
                        rn.Loadi32(), [rn.Reg(rn.Acc()), rn.Name(label)]
                    ),
                    rn.Instr(rn.Add(), [rn.Reg(rn.Acc()), rn.Reg(rn.Cs())]),
                    rn.Instr(rn.Push(), [rn.Reg(rn.Acc())]),
                ]
            case pn.RemoveArguments(pn.Num(arg_size)):
                if int(arg_size) == 0:
                    return self._single_line_comment(stmt, "#")
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Addi(), [rn.Reg(rn.Sp()), rn.Im(arg_size)]),
                ]
            case pn.NewStackframe(pn.Num(local_var_count)):
                instrs = [
                    rn.Instr(rn.Push(), [rn.Reg(rn.Baf())]),
                    rn.Instr(rn.Move(), [rn.Reg(rn.Sp()), rn.Reg(rn.Baf())]),
                    rn.Instr(rn.Subi(), [rn.Reg(rn.Sp()), rn.Im(local_var_count)]),
                ]
                instrs[-1].call_target_function = getattr(
                    stmt, "call_target_function", None
                )
                instrs[-1].indirect_call = getattr(stmt, "indirect_call", False)
                return self._single_line_comment(stmt, "#") + instrs
            case pn.RestoreStackframe():
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Move(), [rn.Reg(rn.Baf()), rn.Reg(rn.Sp())]),
                    rn.Instr(rn.Pop(), [rn.Reg(rn.Baf())]),
                ]
            case pn.RestoreReturnAddress():
                return_instr = rn.Instr(rn.Move(), [rn.Reg(rn.In1()), rn.Reg(rn.Pc())])
                return_instr.return_statement = True
                return self._single_line_comment(stmt, "#") + [
                    rn.Instr(rn.Pop(), [rn.Reg(rn.In1())]),
                    return_instr,
                ]
            case _:
                throw_error(stmt)

    def reti_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(_, blocks):
                ivt_entries = []
                data_entries = []
                if opt_level_1.enabled(global_vars.args):
                    for block in blocks:
                        match block:
                            case pn.Block("_global_inits", _):
                                ivt_entries = opt_level_1.split_interrupt_vector_table_data(
                                    block,
                                    self.symbol_table,
                                    self._char_literal_code,
                                )
                                data_entries = opt_level_1.split_global_inits(
                                    block,
                                    self.symbol_table,
                                    self._char_literal_code,
                                )
                                break

                text_blocks = []
                blocks = [
                    block
                    for block in blocks
                    if not (
                        isinstance(block, pn.Block)
                        and block.name == "_global_inits"
                        and not block.stmts_instrs
                    )
                ]
                for block in blocks:
                    match block:
                        case pn.Block(_, stmts):
                            instrs = []
                            for stmt in stmts:
                                instrs += self._inherit_origin_many(
                                    self._reti_blocks_stmt(stmt), stmt
                                )
                            block.stmts_instrs[:] = instrs
                            if getattr(block, "section", None) == "interrupt_vector_table":
                                ivt_entries.append(block)
                            else:
                                text_blocks.append(block)
                        case _:
                            throw_error(block)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".reti_blocks"),
                    [
                        pn.Section("interrupt_vector_table", ivt_entries),
                        pn.Section("text", text_blocks),
                        pn.Section("data", data_entries),
                    ],
                )
            case _:
                throw_error(file)
