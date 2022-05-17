import global_vars


class N:
    """Nodes"""

    # =========================================================================
    # =                            Container Nodes                            =
    # =========================================================================
    # -------------------------------- Program --------------------------------
    class Program:
        def __init__(self, name, instrs):
            self.name = name
            self.instrs = instrs

        def __repr__(self):
            instrs_str = ""
            for instr in self.instrs:
                instrs_str += f"{instr}"
            return instrs_str

        __match_args__ = ("name", "instrs")

    # ------------------------- Load / Store / Compute ------------------------
    class Instr:
        def __init__(self, op, args):
            self.op = op
            self.args = args

        def __repr__(self):
            instr_str = f"\n{self.op}"
            for arg in self.args:
                instr_str += f" {arg}"
            return instr_str

        __match_args__ = ("op", "args")

    # --------------------------- Jump Instructions ---------------------------
    class Jump:
        def __init__(self, rel, num):
            self.rel = rel
            self.num = num

        def __repr__(self):
            return f"\nJUMP{self.rel} {self.num}"

        __match_args__ = ("rel", "num")

    class Int:
        def __init__(self, num):
            self.num = num

        def __repr__(self):
            return f"\nINT {self.num}"

        __match_args__ = ("num",)

    # ---------------------------- Input and Print ----------------------------
    class Call:
        def __init__(self, name, reg):
            self.name = name
            self.reg = reg

        def __repr__(self):
            return f"\nCALL {self.name} {self.reg}"

        __match_args__ = ("name", "reg")

    # -------------------------------- Comment --------------------------------
    class SingleLineComment:
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return f"\n# {self.val}"

        __match_args__ = ("val",)

    class InlineComment:
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return f'{" " * global_vars.args.distance}  # {self.val}'

        __match_args__ = ("val",)

    # =========================================================================
    # =                              Token Nodes                              =
    # =========================================================================
    # ------------------- Identifier, Immediate and Register ------------------
    class Name:
        # shorter then 'Identifier'
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return self.val

        __match_args__ = ("val",)

    class Num:
        # shorter then 'Immediate'
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return self.val

        __match_args__ = ("val",)

    class Reg:
        def __init__(self, reg):
            self.reg = reg

        def __repr__(self):
            return f"{self.reg}"

        __match_args__ = ("reg",)

    # ----------------------- Compute Memory / Register -----------------------
    class Add:
        def __repr__(self):
            return "ADD"

    class Sub:
        def __repr__(self):
            return "SUB"

    class Mult:
        def __repr__(self):
            return "MULT"

    class Div:
        def __repr__(self):
            return "DIV"

    class Mod:
        def __repr__(self):
            return "MOD"

    class Oplus:
        def __repr__(self):
            return "OPLUS"

    class Or:
        def __repr__(self):
            return "OR"

    class And:
        def __repr__(self):
            return "AND"

    # --------------------- Compute Immediate Instructions --------------------
    class Addi:
        def __repr__(self):
            return "ADDI"

    class Subi:
        def __repr__(self):
            return "SUBI"

    class Multi:
        def __repr__(self):
            return "MULTI"

    class Divi:
        def __repr__(self):
            return "DIVI"

    class Modi:
        def __repr__(self):
            return "MODI"

    class Oplusi:
        def __repr__(self):
            return "OPLUSI"

    class Ori:
        def __repr__(self):
            return "ORI"

    class Andi:
        def __repr__(self):
            return "ANDI"

    # --------------------------- Load Instructions ---------------------------
    class Load:
        def __repr__(self):
            return "LOAD"

    class Loadin:
        def __repr__(self):
            return "LOADIN"

    class Loadi:
        def __repr__(self):
            return "LOADI"

    # --------------------------- Store Instructions --------------------------
    class Store:
        def __repr__(self):
            return "STORE"

    class Storein:
        def __repr__(self):
            return "STOREIN"

    class Move:
        def __repr__(self):
            return "MOVE"

    # ------------------------------- Relations -------------------------------
    class Lt:
        def __repr__(self):
            return "<"

    class LtE:
        def __repr__(self):
            return "<="

    class Gt:
        def __repr__(self):
            return ">"

    class GtE:
        def __repr__(self):
            return ">="

    class Eq:
        def __repr__(self):
            return "=="

    class NEq:
        def __repr__(self):
            return "!="

    class Always:
        def __repr__(self):
            return ""

    class NOp:
        def __repr__(self):
            return "_NOP"

    # --------------------------- Jump Instructions ---------------------------
    class Rti:
        def __repr__(self):
            return "RTI"

    # ------------------------------- Registers -------------------------------
    class Acc:
        def __repr__(self):
            return "ACC"

    class In1:
        def __repr__(self):
            return "IN1"

    class In2:
        def __repr__(self):
            return "IN2"

    class Sp:
        def __repr__(self):
            return "SP"

    class Baf:
        def __repr__(self):
            return "BAF"

    class Cs:
        def __repr__(self):
            return "CS"

    class Ds:
        def __repr__(self):
            return "DS"
