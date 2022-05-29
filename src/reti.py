import global_vars
from ast_node import ASTNode
from reti_nodes import N
from global_funs import bug_in_compiler


class RETI(ASTNode):
    def __init__(self, instrs):
        self.idx = N.Im("0")
        self.regs = {
            "ACC": N.Im("0"),
            "IN1": N.Im("0"),
            "IN2": N.Im("0"),
            "PC": N.Im("0"),
            "PC_SIMPLE": N.Im("0"),
            "SP": N.Im("0"),
            "SP_SIMPLE": N.Im("0"),
            "BAF": N.Im("0"),
            "BAF_SIMPLE": N.Im("0"),
            "CS": N.Im("0"),
            "CS_SIMPLE": N.Im("0"),
            "DS": N.Im("0"),
            "DS_SIMPLE": N.Im("0"),
        }
        self.last_instr = N.Instr(N.Move(), [N.Reg(N.Acc()), N.Reg(N.Pc())])
        self.sram = SRAM(instrs)
        self.uart = UART()
        self.eprom = EPROM()

    def reg_get(self, reg):
        return int(self.regs[reg.upper()].val)

    def reg_set(self, reg, val):
        if reg.upper() == "PC":
            self.regs["PC_SIMPLE"].val = str(val - 2**31)
        if reg.upper() == "SP":
            self.regs["SP_SIMPLE"].val = str(val - 2**31)
        if reg.upper() == "BAF":
            self.regs["BAF_SIMPLE"].val = str(val - 2**31)
        if reg.upper() == "CS":
            self.regs["CS_SIMPLE"].val = str(val - 2**31)
        if reg.upper() == "DS":
            self.regs["DS_SIMPLE"].val = str(val - 2**31)
        self.regs[reg.upper()].val = str(val)

    def reg_increase(self, reg, offset=1):
        self.reg_set(reg, self.reg_get(reg) + offset)

    def save_last_instruction(self):
        self.last_instr = self.sram_get(self.reg_get("PC_Simple"))

    def sram_get(self, addr):
        cell_content = self.sram.cells[addr]
        match cell_content:
            case N.Im(val):
                return int(val)
            case _:
                return cell_content

    def sram_set(self, addr, val):
        self.sram.cells[addr].val = str(val)

    def uart_get(self, addr):
        return int(self.uart.cells[addr].val)

    def uart_set(self, addr, val):
        self.uart.cells[addr].val = str(val)

    def eprom_get(self, addr):
        return int(self.eprom.cells[addr].val)

    def eprom_set(self, addr, val):
        self.eprom.cells[addr].val = str(val)

    def __repr__(self):
        acc = f"{self.__class__.__name__}("
        acc += "\n  {"
        acc += f"\n    index:       {self.idx}"
        acc += f"\n    instruction: " + str(self.last_instr).lstrip()
        for reg in [
            "ACC",
            "IN1",
            "IN2",
            "PC",
            "PC_SIMPLE",
            "SP",
            "SP_SIMPLE",
            "BAF",
            "BAF_SIMPLE",
            "CS",
            "CS_SIMPLE",
            "DS",
            "DS_SIMPLE",
        ]:
            acc += f"\n    {reg}: {' ' * (11-len(reg))}{self.regs[reg]}"
        acc += "\n  }"
        acc += str(self.sram)
        acc += str(self.uart)
        acc += str(self.eprom)
        acc += "\n)" if global_vars.args.verbose else ""
        return acc


class EPROM(ASTNode):
    def __init__(self):
        self.cells = {i: N.Im("0") for i in range(global_vars.eprom_size)}
        super().__init__(visible=[self.cells])

    def __repr__(self):
        acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}"
        acc += "\n    {"
        for addr in range(len(self.cells)):
            acc += (
                "\n      "
                + ("%06i " % addr)
                + ("(%010i): " % addr)
                + str(self.cells[addr])
            )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.verbose else "")


class UART(ASTNode):
    def __init__(self):
        self.cells = {i: N.Im("0") for i in range(global_vars.args.uart_size)}
        super().__init__(visible=[self.cells])

    def __repr__(self):
        acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}"
        acc += "\n    {"
        for addr in range(len(self.cells)):
            acc += (
                "\n      "
                + ("%06i " % addr)
                + ("(%010i): " % (addr + 2**30))
                + str(self.cells[addr])
            )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.verbose else "")


class SRAM(ASTNode):
    def __init__(self, instrs):
        self.instrs = instrs
        start = global_vars.args.process_begin
        end = global_vars.args.process_begin + len(self.instrs) - 1
        min_sram_size = (
            global_vars.args.process_begin
            + len(instrs)
            + global_vars.args.datasegment_size
        )
        self.cells = {
            i: (
                self.instrs[i - global_vars.args.process_begin]
                if i >= start and i <= end
                else N.Im("0")
            )
            for i in range(max(global_vars.args.sram_size, min_sram_size))
        }

    def __repr__(self):
        acc = f"\n  {self.__class__.__name__}" + (
            "(" if global_vars.args.verbose else " "
        )
        acc += "\n    {"
        for addr in range(len(self.cells)):
            acc += (
                "\n      "
                + ("%06i " % addr)
                + ("(%010i): " % (addr + 2**31))
                + str(self.cells[addr]).lstrip()
            )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.verbose else "")
