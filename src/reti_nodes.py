from ast_node import ASTNode
import picoc_nodes as pn
from global_funs import throw_error
from colormanager import ColorManager as CM


# =========================================================================
# =                            Container Nodes                            =
# =========================================================================
# -------------------------------- Program --------------------------------
class Program(ASTNode):
    def __init__(self, name, instrs):
        self.name = name
        self.instrs = instrs
        super().__init__(visible=[self.name, self.instrs])

    def __repr__(self):
        if not self.instrs:
            return ""
        match self.instrs[0]:
            case pn.Block():
                return super().__repr__()
            case _:
                instrs_str = str(self.instrs[0]).replace("\n", "")
                for instr in self.instrs[1:]:
                    instrs_str += f"{instr}"
                return instrs_str

    __match_args__ = ("name", "instrs")


# ------------------------- Load / Store / Compute ------------------------
class Instr(ASTNode):
    def __init__(self, op, args):
        self.op = op
        self.args = args

    def __repr__(self, depth=0):
        instr_str = f"\n{' ' * depth}{CM().BLUE}{self.op}{CM().RESET}"
        for arg in self.args:
            match arg:
                case pn.GoTo():
                    instr_str += " " + arg.__repr__(len(instr_str)).lstrip()
                case _:
                    instr_str += f" {arg}"
        return f"{instr_str}{'' if depth > 0 else ';'}"

    __match_args__ = ("op", "args")


# --------------------------- Jump Instructions ---------------------------
class Jump(ASTNode):
    def __init__(self, rel, im_goto):
        self.rel = rel
        self.im_goto = im_goto

    def __repr__(self, depth=0):
        match self.im_goto:
            case Im():
                return f"\n{' ' * depth}{CM().BLUE}JUMP{CM().RESET}{CM().YELLOW}{self.rel}{CM().RESET} {CM().RED}{self.im_goto}{CM().RESET};"
            case pn.GoTo():
                return (
                    f"\n{' ' * depth}{CM().BLUE}JUMP{CM().RESET}{CM().YELLOW}{self.rel}{CM().RESET} "
                    + f"{CM().RED}"
                    + f"{self.im_goto.__repr__(depth + 4 + 1 + len(str(self.rel)))};".lstrip()
                    + f"{CM().RESET}"
                )
            case _:
                throw_error(self.im_goto)

    __match_args__ = ("rel", "im_goto")


class Int(ASTNode):
    def __repr__(self, depth=0):
        return f"\n{' ' * depth}{CM().BLUE}INT{CM().RESET} {CM().RED}{self.val}{CM().RESET};"

    __match_args__ = ("num",)


# ---------------------------- Input and Print ----------------------------
class Call(ASTNode):
    def __init__(self, name, reg):
        self.name = name
        self.reg = reg

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}{CM().BLUE}CALL{CM().RESET} {self.name} {self.reg};"

    __match_args__ = ("name", "reg")


# =========================================================================
# =                              Token Nodes                              =
# =========================================================================
# ------------------- Identifier, Immediate and Register ------------------
class Name(ASTNode):
    # shorter then 'Identifier'
    def __repr__(self):
        return f"{CM().GREEN}{self.val}{CM().RESET}"


class Im(ASTNode):
    def __repr__(self):
        return f"{CM().RED}{self.val}{CM().RESET}"


class Reg(ASTNode):
    def __init__(self, reg):
        self.reg = reg

    def __repr__(self, depth=0):
        if depth == 0:
            return f"{CM().CYAN}{self.reg}{CM().RESET}"
        else:
            return f"\n{' ' * depth}{CM().CYAN}{self.reg}{CM().RESET}"

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
class Pc(ASTNode):
    def __repr__(self):
        return "PC"


class In1(ASTNode):
    def __repr__(self):
        return "IN1"


class In2(ASTNode):
    def __repr__(self):
        return "IN2"


class Acc(ASTNode):
    def __repr__(self):
        return "ACC"


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
