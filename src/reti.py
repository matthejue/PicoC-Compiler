import global_vars
from ast_node import ASTNode
import reti_nodes as rn
import os


class RETI(ASTNode):
    def __init__(self, instrs):
        # if a '<basename>.datasegment_size' file exists, the value should be
        # taken from there
        if os.path.isfile(
            global_vars.path + global_vars.basename + ".datasegment_size"
        ):
            with open(
                global_vars.path + global_vars.basename + ".datasegment_size",
                "r",
                encoding="utf-8",
            ) as fin:
                global_vars.args.datasegment_size = int(fin.read())
        self.idx = rn.Im("0")
        self.regs = {
            "ACC": rn.Im("0"),
            "ACC_SIMPLE": rn.Im("0"),
            "IN1": rn.Im("0"),
            "IN1_SIMPLE": rn.Im("0"),
            "IN2": rn.Im("0"),
            "IN2_SIMPLE": rn.Im("0"),
            "PC": rn.Im("0"),
            "PC_SIMPLE": rn.Im("0"),
            "SP": rn.Im("0"),
            "SP_SIMPLE": rn.Im("0"),
            "BAF": rn.Im("0"),
            "BAF_SIMPLE": rn.Im("0"),
            "CS": rn.Im("0"),
            "CS_SIMPLE": rn.Im("0"),
            "DS": rn.Im("0"),
            "DS_SIMPLE": rn.Im("0"),
        }
        self.sram = SRAM(instrs)
        self.uart = UART()
        self.eprom = EPROM(len(instrs))
        self.last_instr = None

    def reg_get(self, reg):
        return int(self.regs[reg.upper()].val)

    def reg_set(self, reg, val):
        self.regs[reg.upper()].val = str(val)
        if reg.upper() == "ACC":
            self.regs["ACC_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "IN1":
            self.regs["IN1_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "IN2":
            self.regs["IN2_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "PC":
            self.regs["PC_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "SP":
            self.regs["SP_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "BAF":
            self.regs["BAF_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "CS":
            self.regs["CS_SIMPLE"].val = str(val % 2**30)
        if reg.upper() == "DS":
            self.regs["DS_SIMPLE"].val = str(val % 2**30)

    def reg_increase(self, reg, offset=1):
        self.reg_set(reg, self.reg_get(reg) + offset)

    def do_nothing(self):
        pass

    def save_last_instruction(self):
        addr = self.reg_get("PC")
        self.last_instr = (
            self.sram_get(addr - 2**31)
            if addr >= 2**31
            else self.uart_get(addr - 2**30)
            if addr >= 2**30
            else self.eprom_get(addr)
        )

    def sram_get(self, addr):
        cell_content = self.sram.cells[addr]
        match cell_content:
            case rn.Im(val):
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
        return self.eprom.cells[addr]

    def eprom_set(self, addr, val):
        self.eprom.cells[addr].val = str(val)

    def __repr__(self):
        acc = f"{self.__class__.__name__}("
        acc += "\n  {"
        acc += f"\n    index:       {self.idx}"
        acc += f"\n    instruction: " + str(self.last_instr).lstrip()
        for reg in self.regs.keys():
            acc += f"\n    {reg}: {' ' * (11-len(reg))}{self.regs[reg]}"
        acc += "\n  }"
        acc_addr = self.reg_get("ACC")
        in1_addr = self.reg_get("IN1")
        in2_addr = self.reg_get("IN2")
        pc_addr = self.reg_get("PC")
        sp_addr = self.reg_get("SP")
        baf_addr = self.reg_get("BAF")
        cs_addr = self.reg_get("CS")
        ds_addr = self.reg_get("DS")
        acc += self.sram.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        acc += self.uart.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        acc += self.eprom.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        acc += "\n)" if global_vars.args.double_verbose else ""
        return acc


class EPROM(ASTNode):
    def __init__(self, len_instrs):
        self.cells = {
            0: rn.Instr(rn.Loadi(), [rn.Reg(rn.Ds()), rn.Im(str(-(2**21)))]),
            1: rn.Instr(rn.Multi(), [rn.Reg(rn.Ds()), rn.Im(str(2**10))]),
            2: rn.Instr(rn.Move(), [rn.Reg(rn.Ds()), rn.Reg(rn.Sp())]),
            3: rn.Instr(rn.Move(), [rn.Reg(rn.Ds()), rn.Reg(rn.Cs())]),
            4: rn.Instr(
                rn.Addi(),
                [
                    rn.Reg(rn.Sp()),
                    rn.Im(
                        str(
                            global_vars.args.process_begin
                            + len_instrs
                            + global_vars.args.datasegment_size
                            - 1
                        )
                    ),
                ],
            ),
            5: rn.Instr(
                rn.Addi(),
                [rn.Reg(rn.Cs()), rn.Im(str(global_vars.args.process_begin))],
            ),
            6: rn.Instr(
                rn.Addi(),
                [
                    rn.Reg(rn.Ds()),
                    rn.Im(str(global_vars.args.process_begin + len_instrs)),
                ],
            ),
            7: rn.Instr(rn.Move(), [rn.Reg(rn.Cs()), rn.Reg(rn.Pc())]),
        }
        super().__init__(visible=[self.cells])

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.double_verbose else ' '}"
        acc += "\n    {"
        acc += print_cells(
            self.cells,
            0,
            acc_addr,
            in1_addr,
            in2_addr,
            pc_addr,
            sp_addr,
            baf_addr,
            cs_addr,
            ds_addr,
        )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.double_verbose else "")


class UART(ASTNode):
    def __init__(self):
        self.cells = {i: rn.Im("0") for i in range(global_vars.uart_size)}
        super().__init__(visible=[self.cells])

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.double_verbose else ' '}"
        acc += "\n    {"
        acc += print_cells(
            self.cells,
            2**30,
            acc_addr,
            in1_addr,
            in2_addr,
            pc_addr,
            sp_addr,
            baf_addr,
            cs_addr,
            ds_addr,
        )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.double_verbose else "")


class SRAM(ASTNode):
    def __init__(self, instrs):
        start = global_vars.args.process_begin
        end = global_vars.args.process_begin + len(instrs) - 1
        min_sram_size = (
            global_vars.args.process_begin
            + len(instrs)
            + global_vars.args.datasegment_size
        )
        self.cells = {
            i: (
                instrs[i - global_vars.args.process_begin]
                if i >= start and i <= end
                else rn.Im("0")
            )
            for i in range(min_sram_size)
        }

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n  {self.__class__.__name__}{'(' if global_vars.args.double_verbose else ' '}"
        acc += "\n    {"
        acc += print_cells(
            self.cells,
            2**31,
            acc_addr,
            in1_addr,
            in2_addr,
            pc_addr,
            sp_addr,
            baf_addr,
            cs_addr,
            ds_addr,
        )
        acc += "\n    }"
        return acc + ("\n  )" if global_vars.args.double_verbose else "")


def print_cells(
    cells,
    constant,
    acc_addr,
    in1_addr,
    in2_addr,
    pc_addr,
    sp_addr,
    baf_addr,
    cs_addr,
    ds_addr,
):
    acc = ""
    for addr in range(len(cells)):
        acc += (
            "\n      "
            + ("%06i " % addr)
            #  + ("(%010i): " % (addr + constant))
            + str(cells[addr]).lstrip()
            + (" <- ACC" if addr == acc_addr - constant else "")
            + (" <- IN1" if addr == in1_addr - constant else "")
            + (" <- IN2" if addr == in2_addr - constant else "")
            + (" <- PC" if addr == pc_addr - constant else "")
            + (" <- SP" if addr == sp_addr - constant else "")
            + (" <- BAF" if addr == baf_addr - constant else "")
            + (" <- CS" if addr == cs_addr - constant else "")
            + (" <- DS" if addr == ds_addr - constant else "")
        )
    return acc
