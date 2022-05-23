import global_vars
from ast_node import ASTNode
from picoc_nodes import N as PN


class N(ASTNode):
    """Nodes"""

    # =========================================================================
    # =                            Container Nodes                            =
    # =========================================================================
    # -------------------------------- Program --------------------------------
    class Program(ASTNode):
        def __init__(self, name, instrs_blocks):
            self.name = name
            self.instrs_blocks = instrs_blocks
            super().__init__(children=[self.name, self.instrs_blocks])

        def __repr__(self):
            if not self.instrs_blocks:
                return ""
            match self.instrs_blocks[0]:
                case PN.Block():
                    return super().__repr__()
                case _:
                    instrs_str = str(self.instrs_blocks[0]).replace("\n", "")
                    for instr in self.instrs_blocks[1:]:
                        instrs_str += f"{instr}"
                    return instrs_str

        __match_args__ = ("name", "instrs_blocks")

    # ------------------------- Load / Store / Compute ------------------------
    class Instr(ASTNode):
        def __init__(self, op, args):
            self.op = op
            self.args = args

        def __repr__(self, depth=0):
            instr_str = f"\n{' ' * depth}{self.op}"
            for arg in self.args:
                instr_str += f" {arg}"
            return f"{instr_str};"

        __match_args__ = ("op", "args")

    # --------------------------- Jump Instructions ---------------------------
    class Jump(ASTNode):
        def __init__(self, rel, num):
            self.rel = rel
            self.num = num

        def __repr__(self, depth=0):
            return f"\n{' ' * depth}JUMP{self.rel} {self.num};"

        __match_args__ = ("rel", "num")

    class Int(ASTNode):
        def __init__(self, num):
            self.num = num

        def __repr__(self, depth=0):
            return f"\n{' ' * depth}INT {self.num};"

        __match_args__ = ("num",)

    # ---------------------------- Input and Print ----------------------------
    class Call(ASTNode):
        def __init__(self, name, reg):
            self.name = name
            self.reg = reg

        def __repr__(self, depth=0):
            return f"\n{' ' * depth}CALL {self.name} {self.reg};"

        __match_args__ = ("name", "reg")

    # -------------------------------- Comment --------------------------------
    class SingleLineComment(ASTNode):
        def __init__(self, val):
            self.val = val

        def __repr__(self, depth=0):
            return f"\n{' ' * depth}# {self.val}"

        __match_args__ = ("val",)

    class InlineComment(ASTNode):
        def __init__(self, val):
            self.val = val

        def __repr__(self, depth=0):
            return f'{" " * global_vars.args.gap}  # {self.val}'

        __match_args__ = ("val",)

    # =========================================================================
    # =                              Token Nodes                              =
    # =========================================================================
    # ------------------- Identifier, Immediate and Register ------------------
    class Name(ASTNode):
        # shorter then 'Identifier'
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return self.val

        __match_args__ = ("val",)

    class Im(ASTNode):
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return self.val

        __match_args__ = ("val",)

    class Reg(ASTNode):
        def __init__(self, reg):
            self.reg = reg

        def __repr__(self):
            return f"{self.reg}"

        __match_args__ = ("reg",)

    # ----------------------- Compute Memory / Register -----------------------
    class Add(ASTNode):
        def __repr__(self):
            return "ADD"

    class Sub(ASTNode):
        def __repr__(self):
            return "SUB"

    class Mult(ASTNode):
        def __repr__(self):
            return "MULT"

    class Div(ASTNode):
        def __repr__(self):
            return "DIV"

    class Mod(ASTNode):
        def __repr__(self):
            return "MOD"

    class Oplus(ASTNode):
        def __repr__(self):
            return "OPLUS"

    class Or(ASTNode):
        def __repr__(self):
            return "OR"

    class And(ASTNode):
        def __repr__(self):
            return "AND"

    # --------------------- Compute Immediate Instructions --------------------
    class Addi(ASTNode):
        def __repr__(self):
            return "ADDI"

    class Subi(ASTNode):
        def __repr__(self):
            return "SUBI"

    class Multi(ASTNode):
        def __repr__(self):
            return "MULTI"

    class Divi(ASTNode):
        def __repr__(self):
            return "DIVI"

    class Modi(ASTNode):
        def __repr__(self):
            return "MODI"

    class Oplusi(ASTNode):
        def __repr__(self):
            return "OPLUSI"

    class Ori(ASTNode):
        def __repr__(self):
            return "ORI"

    class Andi(ASTNode):
        def __repr__(self):
            return "ANDI"

    # --------------------------- Load Instructions ---------------------------
    class Load(ASTNode):
        def __repr__(self):
            return "LOAD"

    class Loadin(ASTNode):
        def __repr__(self):
            return "LOADIN"

    class Loadi(ASTNode):
        def __repr__(self):
            return "LOADI"

    # --------------------------- Store Instructions --------------------------
    class Store(ASTNode):
        def __repr__(self):
            return "STORE"

    class Storein(ASTNode):
        def __repr__(self):
            return "STOREIN"

    class Move(ASTNode):
        def __repr__(self):
            return "MOVE"

    # ------------------------------- Relations -------------------------------
    class Lt(ASTNode):
        def __repr__(self):
            return "<"

    class LtE(ASTNode):
        def __repr__(self):
            return "<="

    class Gt(ASTNode):
        def __repr__(self):
            return ">"

    class GtE(ASTNode):
        def __repr__(self):
            return ">="

    class Eq(ASTNode):
        def __repr__(self):
            return "=="

    class NEq(ASTNode):
        def __repr__(self):
            return "!="

    class Always(ASTNode):
        def __repr__(self):
            return ""

    class NOp(ASTNode):
        def __repr__(self):
            return "_NOP"

    # --------------------------- Jump Instructions ---------------------------
    class Rti(ASTNode):
        def __repr__(self):
            return "RTI"

    # ------------------------------- Registers -------------------------------
    class Acc(ASTNode):
        def __repr__(self):
            return "ACC"

    class In1(ASTNode):
        def __repr__(self):
            return "IN1"

    class In2(ASTNode):
        def __repr__(self):
            return "IN2"

    class Sp(ASTNode):
        def __repr__(self):
            return "SP"

    class Baf(ASTNode):
        def __repr__(self):
            return "BAF"

    class Cs(ASTNode):
        def __repr__(self):
            return "CS"

    class Ds(ASTNode):
        def __repr__(self):
            return "DS"
