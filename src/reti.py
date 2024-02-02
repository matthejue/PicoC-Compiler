import global_vars
from ast_node import ASTNode
import reti_nodes as rn
import os
from colormanager import ColorManager as CM


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
        self.round = 0
        self.regs = {
            "ACC": 0,
            "ACC_SIMPLE": 0,
            "IN1": 0,
            "IN1_SIMPLE": 0,
            "IN2": 0,
            "IN2_SIMPLE": 0,
            "PC": 0,
            "PC_SIMPLE": 0,
            "SP": 0,
            "SP_SIMPLE": 0,
            "BAF": 0,
            "BAF_SIMPLE": 0,
            "CS": 0,
            "CS_SIMPLE": 0,
            "DS": 0,
            "DS_SIMPLE": 0,
        }
        self.sram = SRAM(instrs)
        self.uart = UART()
        self.eprom = EPROM(len(instrs))
        self.last_instr = None

        # deal with uart receive register and status register files
        if os.path.isfile(global_vars.path + global_vars.basename + ".uart_r"):
            with open(
                global_vars.path + global_vars.basename + ".uart_s",
                "r",
                encoding="utf-8",
            ) as fin_s, open(
                global_vars.path + global_vars.basename + ".uart_r",
                "r",
                encoding="utf-8",
            ) as fin_r:
                self.uart_s = list(
                    reversed(
                        [
                            int(line)
                            for line in fin_s.readline().replace("\n", "").split(" ")
                            if line.isdigit()
                        ]
                    )
                )
                self.uart_r = list(
                    reversed(
                        [
                            int(line)
                            for line in fin_r.readline().replace("\n", "").split(" ")
                            if line.isdigit()
                        ]
                    )
                )
        else:
            self.uart_r = []
            self.uart_s = []
        self.status_register_lock = False

    def reg_get(self, reg):
        return self.regs[reg]

    def reg_set(self, reg, val):
        self.regs[reg] = val
        if reg == "ACC":
            self.regs["ACC_SIMPLE"] = val % 2**30
        if reg == "IN1":
            self.regs["IN1_SIMPLE"] = val % 2**30
        if reg == "IN2":
            self.regs["IN2_SIMPLE"] = val % 2**30
        if reg == "PC":
            self.regs["PC_SIMPLE"] = val % 2**30
        if reg == "SP":
            self.regs["SP_SIMPLE"] = val % 2**30
        if reg == "BAF":
            self.regs["BAF_SIMPLE"] = val % 2**30
        if reg == "CS":
            self.regs["CS_SIMPLE"] = val % 2**30
        if reg == "DS":
            self.regs["DS_SIMPLE"] = val % 2**30

    def reg_increase(self, reg, offset=1):
        self.reg_set(reg, self.regs[reg] + offset)

    def do_nothing(self):
        pass

    def save_last_instruction(self):
        addr = self.regs["PC"]
        self.last_instr = (
            self.sram_get(addr - 2**31)
            if addr >= 2**31
            else self.uart_get(addr - 2**30)
            if addr >= 2**30
            else self.eprom_get(addr)
        )

    def sram_get(self, addr):
        return self.sram.cells[addr]

    def sram_set(self, addr, val):
        self.sram.cells[addr] = val

    def uart_get(self, addr):
        if addr == 1 and len(self.uart_r) > 0:
            r_reg = self.uart_r.pop()
            if r_reg > 2**8 - 1:
                print(
                    f"The value {r_reg} for the uart receive register needs more than 8 bit."
                )
            self.uart.cells[addr] = r_reg
        elif addr == 2 and len(self.uart_s) > 0 and not self.status_register_lock:
            s_reg = self.uart_s.pop()
            if s_reg > 2**8 - 1:
                print(
                    f"The value {s_reg} for the uart status register needs more than 8 bit."
                )
            self.uart.cells[addr] = self.uart.cells[addr] | s_reg
            if s_reg & 2:
                self.status_register_lock = True
        return self.uart.cells[addr]

    def uart_set(self, addr, val):
        self.uart.cells[addr] = val
        if addr == 2 and not val & 2:
            self.status_register_lock = False

    def eprom_get(self, addr):
        return self.eprom.cells[addr]

    def eprom_set(self, addr, val):
        self.eprom.cells[addr] = val

    def __repr__(self):
        global_vars.next_as_normal = True
        acc = (
            "\n" if self.round > 1 else ""
        ) + f"{CM().GREEN}index:{CM().RESET}       {self.round}"
        global_vars.next_as_normal = False
        acc += (
            f"\n{CM().GREEN}instruction:{CM().RESET} " + str(self.last_instr).lstrip()
        )
        for reg in self.regs.keys():
            if reg in [
                "PC",
                "PC_SIMPLE",
                "SP",
                "SP_SIMPLE",
                "BAF",
                "BAF_SIMPLE",
                "CS",
                "CS_SIMPLE",
                "BAF",
                "BAF_SIMPLE",
            ]:
                global_vars.next_as_normal = True
            acc += f"\n{CM().GREEN}{reg}:{CM().RESET} {' ' * (11-len(reg))}{self.regs[reg]}"
            global_vars.next_as_normal = False
        acc_addr = self.regs["ACC"]
        in1_addr = self.regs["IN1"]
        in2_addr = self.regs["IN2"]
        pc_addr = self.regs["PC"]
        sp_addr = self.regs["SP"]
        baf_addr = self.regs["BAF"]
        cs_addr = self.regs["CS"]
        ds_addr = self.regs["DS"]
        acc += self.sram.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        acc += self.uart.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        acc += self.eprom.__repr__(
            acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
        )
        return acc

    def regs_str(self):
        acc = ""
        for reg in self.regs.keys():
            acc += f"\n{reg}: {' ' * (11-len(reg))}{self.regs[reg]}"
        return acc

    def eprom_str(self):
        return self.cells_str(self.eprom.cells, 0)

    def uart_str(self):
        return self.cells_str(self.uart.cells, 2**30)

    def sram_str(self):
        return self.cells_str(self.sram.cells, 2**31)

    def cells_str(self, cells, constant):
        acc = ""
        for addr in range(len(cells)):
            acc += (
                "\n  "
                + (f"%05i " % addr)
                + (
                    ("(%010i): " % (addr + constant))
                    if global_vars.args.double_verbose
                    else ""
                )
                + str(cells[addr]).lstrip()
                + (f" <- ACC" if addr == self.regs["ACC"] - constant else "")
                + (f" <- IN1" if addr == self.regs["IN1"] - constant else "")
                + (f" <- IN2" if addr == self.regs["IN2"] - constant else "")
                + (f" <- PC" if addr == self.regs["PC"] - constant else "")
                + (f" <- SP" if addr == self.regs["SP"] - constant else "")
                + (f" <- BAF" if addr == self.regs["BAF"] - constant else "")
                + (f" <- CS" if addr == self.regs["CS"] - constant else "")
                + (f" <- DS" if addr == self.regs["DS"] - constant else "")
            )
        return acc


class EPROM(ASTNode):
    def __init__(self, len_instrs):
        self.cells = {
            0: rn.Instr(rn.Loadi(), [rn.Reg(rn.Ds()), rn.Im(str(-(2**21)))]),
            1: rn.Instr(rn.Multi(), [rn.Reg(rn.Ds()), rn.Im(str(2**10))]),
            2: rn.Instr(rn.Move(), [rn.Reg(rn.Ds()), rn.Reg(rn.Sp())]),
            3: rn.Instr(rn.Move(), [rn.Reg(rn.Ds()), rn.Reg(rn.Baf())]),
            4: rn.Instr(rn.Move(), [rn.Reg(rn.Ds()), rn.Reg(rn.Cs())]),
            5: rn.Instr(
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
            6: rn.Instr(rn.Addi(), [rn.Reg(rn.Baf()), rn.Im("2")]),
            7: rn.Instr(
                rn.Addi(),
                [rn.Reg(rn.Cs()), rn.Im(str(global_vars.args.process_begin))],
            ),
            8: rn.Instr(
                rn.Addi(),
                [
                    rn.Reg(rn.Ds()),
                    rn.Im(str(global_vars.args.process_begin + len_instrs)),
                ],
            ),
            9: rn.Instr(rn.Move(), [rn.Reg(rn.Cs()), rn.Reg(rn.Pc())]),
        }
        super().__init__(visible=[self.cells])

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n{CM().GREEN}{self.__class__.__name__}:{CM().RESET}"  # {'(' if global_vars.args.double_verbose else ' '}"
        # acc += "\n{"
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
        return acc  # + "\n}"
        #  return acc + ("\n  )" if global_vars.args.double_verbose else "")


class UART(ASTNode):
    def __init__(self):
        self.cells = {i: 0 for i in range(global_vars.uart_size)}
        super().__init__(visible=[self.cells])

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n{CM().GREEN}{self.__class__.__name__}:{CM().RESET}"  # {'(' if global_vars.args.double_verbose else ' '}"
        #  acc += "\n{"
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
        return acc  # + "\n  }"
        #  return acc + ("\n  )" if global_vars.args.double_verbose else "")


class SRAM(ASTNode):
    def __init__(self, instrs):
        term_process = {
            0: rn.Jump(rn.Always(), rn.Im("0")),
            1: 2**31,
        }
        start = max(global_vars.args.process_begin, len(term_process))
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
                else term_process[i]
                if i < len(term_process)
                else 0
            )
            for i in range(min_sram_size)
        }

    def __repr__(
        self, acc_addr, in1_addr, in2_addr, pc_addr, sp_addr, baf_addr, cs_addr, ds_addr
    ):
        acc = f"\n{CM().GREEN}{self.__class__.__name__}:{CM().RESET}"  # {'(' if global_vars.args.double_verbose else ' '}"
        #  acc += "\n{"
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
        return acc  # + "\n}"
        #  return acc + ("\n  )" if global_vars.args.double_verbose else "")


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
            "\n  "
            + (f"{CM().GREEN}%05i{CM().RESET} " % addr)
            + (
                ("(%010i): " % (addr + constant))
                if global_vars.args.double_verbose
                else ""
            )
            + str(cells[addr]).lstrip()
            + (
                f" {CM().GREEN}<- ACC{CM().RESET}"
                if addr == acc_addr - constant
                else ""
            )
            + (
                f" {CM().GREEN}<- IN1{CM().RESET}"
                if addr == in1_addr - constant
                else ""
            )
            + (
                f" {CM().GREEN}<- IN2{CM().RESET}"
                if addr == in2_addr - constant
                else ""
            )
            + (f" {CM().GREEN}<- PC{CM().RESET}" if addr == pc_addr - constant else "")
            + (f" {CM().GREEN}<- SP{CM().RESET}" if addr == sp_addr - constant else "")
            + (
                f" {CM().GREEN}<- BAF{CM().RESET}"
                if addr == baf_addr - constant
                else ""
            )
            + (f" {CM().GREEN}<- CS{CM().RESET}" if addr == cs_addr - constant else "")
            + (f" {CM().GREEN}<- DS{CM().RESET}" if addr == ds_addr - constant else "")
        )
    return acc
