import reti_nodes as rn
import picoc_nodes as pn
from reti import RETI
import global_vars
from util_funs import (
    bug_in_interpreter,
    filter_out_comments,
)
from ctypes import c_int32, c_uint32
from colormanager import ColorManager as CM
from daemon import Deamon
import sys


class RETIInterpreter:
    def __init__(self, program: rn.Program):
        # when the <outabse>.out file gets written for the first time it should
        # overwrite everything else
        self.program = program
        match self.program:
            case rn.Program(_, instrs):
                self.reti = RETI(list(filter_out_comments(instrs)))
            case _:
                bug_in_interpreter(self.program)
        self.first_out = True
        self.first_reti_state = True
        self.daemon = Deamon()

    def _jump_condition(self, condition, offset):
        if condition:
            self.reti.reg_increase("PC", offset)
        else:
            self.reti.reg_increase("PC")

    def _op(self, opd1, op, opd2):
        match op:
            case (rn.Add() | rn.Addi()):
                return c_int32(c_int32(opd1).value + c_int32(opd2).value).value
            case (rn.Sub() | rn.Subi()):
                return c_int32(c_int32(opd1).value - c_int32(opd2).value).value
            case (rn.Mult() | rn.Multi()):
                return c_int32(c_int32(opd1).value * c_int32(opd2).value).value
            case (rn.Div() | rn.Divi()):
                return c_int32(c_int32(opd1).value // c_int32(opd2).value).value
            case (rn.Mod() | rn.Modi()):
                return c_int32(c_int32(opd1).value % c_int32(opd2).value).value
            case (rn.Oplus() | rn.Oplusi()):
                return c_uint32(c_uint32(opd1).value ^ c_uint32(opd2).value).value
            case (rn.Or() | rn.Ori()):
                return c_uint32(c_uint32(opd1).value | c_uint32(opd2).value).value
            case (rn.And() | rn.Andi()):
                return c_uint32(c_uint32(opd1).value & c_uint32(opd2).value).value
            case _:
                bug_in_interpreter(op)

    def _memory_store(self, destination, source):
        source = c_uint32(source).value
        match destination:
            # addressbus
            case rn.Im(val):
                higher_bits = (
                    self.reti.regs["DS"] & 0b11111111_11000000_00000000_00000000
                )
                memory_type = self.reti.regs["DS"] >> 30
                match memory_type:
                    case 0b00:
                        # error, eprom is readonly
                        self.reti.eprom_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b01000000_00000000_00000000_00000000,
                            source,
                        )
                    case 0b01:
                        self.reti.uart_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b01000000_00000000_00000000_00000000,
                            source,
                        )
                    case (0b10 | 0b11):
                        self.reti.sram_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b10000000_00000000_00000000_00000000,
                            source,
                        )
                    case _:
                        bug_in_interpreter(memory_type)
            case rn.Reg(reg):
                self.reti.reg_set(str(reg), source)
            # right_databus
            case int():
                destination = c_uint32(destination).value
                memory_type = destination >> 30
                match memory_type:
                    case 0b00:
                        # error, eprom is readonly
                        self.reti.eprom_set(((destination << 2) % 2**32) >> 2, source)
                    case 0b01:
                        self.reti.uart_set(((destination << 2) % 2**32) >> 2, source)
                    case (0b10 | 0b11):
                        self.reti.sram_set(((destination << 2) % 2**32) >> 2, source)
                    case _:
                        bug_in_interpreter(memory_type)
            case _:
                bug_in_interpreter(destination)

    def _memory_load(self, source) -> int:
        match source:
            # addressbus
            case rn.Im(val):
                higher_bits = (
                    self.reti.regs["DS"] & 0b11111111_11000000_00000000_00000000
                )
                memory_type = self.reti.regs["DS"] >> 30
                match memory_type:
                    case 0b00:
                        return self.reti.eprom_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b01000000_00000000_00000000_00000000
                        )
                    case 0b01:
                        return self.reti.uart_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b01000000_00000000_00000000_00000000
                        )
                    case (0b10 | 0b11):
                        return self.reti.sram_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits % 0b10000000_00000000_00000000_00000000
                        )
                    case _:
                        bug_in_interpreter(memory_type)

            case rn.Reg(reg):
                return self.reti.regs[str(reg)]
            # right databus
            case int():
                source = c_uint32(source).value
                memory_type = source >> 30
                match memory_type:
                    case 0b00:
                        return self.reti.eprom_get(((source << 2) % 2**32) >> 2)
                    case 0b01:
                        return self.reti.uart_get(((source << 2) % 2**32) >> 2)
                    case (0b10 | 0b11):
                        return self.reti.sram_get(((source << 2) % 2**32) >> 2)
                    case _:
                        bug_in_interpreter(memory_type)
            case _:
                bug_in_interpreter(source)

    def _instr(self, instr):
        match instr:
            case pn.RETIComment():
                self.reti.reg_increase("PC")
            case rn.Instr(
                operation,
                [rn.Reg() as destination, (rn.Im() | rn.Reg()) as source],
            ) if type(operation) in global_vars.COMPUTE_INSTRUCTION:
                self._memory_store(
                    destination,
                    self._op(
                        self._memory_load(destination),
                        operation,
                        self._memory_load(source),
                    ),
                )
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Instr(operation, [rn.Reg() as destination, rn.Im(val)]) if type(
                operation
            ) in global_vars.COMPUTE_IMMEDIATE_INSTRUCTION:
                self._memory_store(
                    destination,
                    self._op(self._memory_load(destination), operation, int(val)),
                )
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Instr(rn.Load(), [rn.Reg() as destination, rn.Im() as source]):
                self._memory_store(destination, self._memory_load(source))
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Instr(
                rn.Loadin(),
                [rn.Reg() as reg_source, rn.Reg() as destination, rn.Im(val)],
            ):
                self._memory_store(
                    destination,
                    self._memory_load(
                        self._memory_load(reg_source) + int(val),
                    ),
                )
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Instr(rn.Loadi(), [rn.Reg() as destination, rn.Im(val)]):
                self._memory_store(
                    destination,
                    c_uint32(int(val)).value % 0b1000000_00000000_00000000,
                )
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Instr(rn.Store(), [rn.Reg() as source, rn.Im() as destination]):
                self._memory_store(destination, self._memory_load(source))
                self.reti.reg_increase("PC")
            case rn.Instr(
                rn.Storein(),
                [rn.Reg() as destination, rn.Reg() as reg_source, rn.Im(val)],
            ):
                self._memory_store(
                    self._memory_load(destination) + int(val),
                    self._memory_load(reg_source),
                )
                self.reti.reg_increase("PC")
            case rn.Instr(rn.Move(), [rn.Reg() as source, rn.Reg() as destination]):
                self._memory_store(destination, self._memory_load(source))
                self.reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else self.reti.do_nothing()
            case rn.Jump(rel, rn.Im(val)):
                match rel:
                    case rn.Lt():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value < 0, int(val)
                        )
                    case rn.LtE():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value <= 0, int(val)
                        )
                    case rn.Gt():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value > 0, int(val)
                        )
                    case rn.GtE():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value >= 0, int(val)
                        )
                    case rn.Eq():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value == 0, int(val)
                        )
                    case rn.NEq():
                        self._jump_condition(
                            c_int32(self.reti.regs["ACC"]).value != 0, int(val)
                        )
                    case rn.Always():
                        self._jump_condition(True, int(val))
                    case rn.NOp():
                        self._jump_condition(False, int(val))
                    case _:
                        bug_in_interpreter(rel)
            #  case rn.Int(rn.Im(val)):
            #      # save PC to stack
            #      self.reti.sram_set(self.reti.regs["SP"], c_uint32(self.reti.regs["PC"]).value)
            #      self.reti.reg_set("SP", c_uint32(self.reti.regs["SP"]).value - 1)
            #      # jump to start address of isr
            #      self.reti.reg_set("PC", self._memory_load(int(val) + 2**31))
            #  case rn.Rti():
            #      # restore PC
            #      self.reti.reg_set(
            #          "PC", self.reti.sram_get(c_uint32(self.reti.regs["SP"]).value + 1)
            #      )
            #      # delete PC from stack
            #      self.reti.reg_set("SP", c_uint32(self.reti.regs["SP"]).value + 1)
            case rn.Call(rn.Name("PRINT"), rn.Reg(reg)):
                print(
                    f"{CM().GREEN}Output:{CM().RESET} {CM().RED}{c_int32(self.reti.regs[str(reg)]).value}{CM().RESET}"
                )
                if global_vars.path:
                    if self.first_out:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "w",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(str(c_int32(self.reti.regs[str(reg)]).value))
                        self.first_out = False
                    else:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "a",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(
                                " " + str(c_int32(self.reti.regs[str(reg)]).value)
                            )
                self.reti.reg_increase("PC")
            case rn.Call(rn.Name("INPUT"), rn.Reg(reg)):
                if global_vars.input:
                    self.reti.reg_set(str(reg), c_uint32(global_vars.input.pop()).value)
                else:
                    self.reti.reg_set(str(reg), c_uint32(int(input("Input:"))).value)
                self.reti.reg_increase("PC")
            case _:
                bug_in_interpreter(instr)

    def _instrs(self):
        while True:
            if global_vars.args.plugin_support:
                self.daemon.cont(self.reti)

            addr = self.reti.regs["PC"]
            if addr >= 2**31:
                i = addr - 2**31
                next_instruction = self.reti.sram_get(i)
            elif addr >= 2**30:
                i = addr - 2**30
                next_instruction = self.reti.uart_get(i)
            else:  # addr < 2**30
                i = addr
                next_instruction = self.reti.eprom_get(i)
            match next_instruction:
                case rn.Jump(rn.Always(), rn.Im("0")):
                    self._finalize()
                    break
                case int():
                    self._finalize()
                    break
                case _:
                    self.reti.save_last_instruction()
                    self._instr(next_instruction)
                    if global_vars.args.intermediate_stages and (
                        global_vars.args.verbose or global_vars.args.double_verbose
                    ):
                        self._reti_state_option()

    def _finalize(self):
        if global_vars.args.intermediate_stages and not (
            global_vars.args.verbose or global_vars.args.double_verbose
        ):
            self._reti_state_option()
            # in case of an print call as last instruction with the --verbose
            # option, the reti state was already printed
        # needs a newline at the end, else it differs from .out_expected
        if global_vars.path:
            if self.first_out:
                with open(
                    global_vars.path + global_vars.basename + ".out",
                    "w",
                    encoding="utf-8",
                ) as fout:
                    fout.write("\n")
                    self.first_out = False
            else:
                with open(
                    global_vars.path + global_vars.basename + ".out",
                    "a",
                    encoding="utf-8",
                ) as fout:
                    fout.write("\n")

    def _reti_state_option(self):
        self.reti.round = self.reti.round + 1
        if global_vars.args.print:
            print(self.reti)

        CM().color_off()

        if global_vars.path:
            if self.first_reti_state:
                with open(
                    global_vars.path + global_vars.basename + ".reti_states",
                    "w",
                    encoding="utf-8",
                ) as fout:
                    fout.write(str(self.reti))
                self.first_reti_state = False
            else:
                with open(
                    global_vars.path + global_vars.basename + ".reti_states",
                    "a",
                    encoding="utf-8",
                ) as fout:
                    fout.write("\n" + str(self.reti))

        if global_vars.args.color:
            CM().color_on()
        else:
            CM().color_off()

    def interp_reti(self):
        self._instrs()
