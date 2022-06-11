import reti_nodes as rn
from reti import RETI
import global_vars
from global_funs import (
    bug_in_interpreter,
    remove_extension,
    filter_out_comments,
)
import os
from ctypes import c_int32, c_uint32


class RETIInterpreter:
    def __init__(self):
        # when the <outabse>.out file gets written for the first time it should
        # overwrite everything else
        self.first_out = True
        self.first_reti_state = True
        self.test_input = []

    def _jump_condition(self, condition, offset, reti: RETI):
        if condition:
            reti.reg_increase("PC", offset)
        else:
            reti.reg_increase("PC")

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

    def _memory_store(self, destination, source, reti: RETI):
        source = c_uint32(source).value
        match destination:
            # addressbus
            case rn.Im(val):
                higher_bits = (reti.reg_get("DS") >> 22) % 0b100000000 << 22
                memory_type = reti.reg_get("DS") >> 30
                match memory_type:
                    case 0b00:
                        # error, eprom is readonly
                        reti.eprom_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits,
                            source,
                        )
                    case 0b01:
                        reti.uart_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits,
                            source,
                        )
                    case (0b10 | 0b11):
                        reti.sram_set(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits,
                            source,
                        )
                    case _:
                        bug_in_interpreter(memory_type)
            case rn.Reg(reg):
                reti.reg_set(str(reg), source)
            # right_databus
            case int():
                destination = c_uint32(destination).value
                memory_type = destination >> 30
                match memory_type:
                    case 0b00:
                        # error, eprom is readonly
                        reti.eprom_set(((destination << 2) % 2**32) >> 2, source)
                    case 0b01:
                        reti.uart_set(((destination << 2) % 2**32) >> 2, source)
                    case (0b10 | 0b11):
                        reti.sram_set(((destination << 2) % 2**32) >> 2, source)
                    case _:
                        bug_in_interpreter(memory_type)
            case _:
                bug_in_interpreter(destination)

    def _memory_load(self, source, reti) -> int:
        match source:
            # addressbus
            case rn.Im(val):
                higher_bits = (reti.reg_get("DS") >> 22) % 0b100000000 << 22
                memory_type = reti.reg_get("DS") >> 30
                match memory_type:
                    case 0b00:
                        return reti.eprom_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits
                        )
                    case 0b01:
                        return reti.uart_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits
                        )
                    case (0b10 | 0b11):
                        return reti.sram_get(
                            c_uint32(int(val)).value % 0b1000000_00000000_00000000
                            + higher_bits
                        )
                    case _:
                        bug_in_interpreter(memory_type)

            case rn.Reg(reg):
                return reti.reg_get(str(reg))
            # right databus
            case int():
                source = c_uint32(source).value
                memory_type = source >> 30
                match memory_type:
                    case 0b00:
                        return reti.eprom_get(((source << 2) % 2**32) >> 2)
                    case 0b01:
                        return reti.uart_get(((source << 2) % 2**32) >> 2)
                    case (0b10 | 0b11):
                        return reti.sram_get(((source << 2) % 2**32) >> 2)
                    case _:
                        bug_in_interpreter(memory_type)
            case _:
                bug_in_interpreter(source)

    def _instr(self, instr, reti: RETI):
        match instr:
            case rn.Instr(
                operation,
                [rn.Reg() as destination, (rn.Im() | rn.Reg()) as source],
            ) if type(operation) in global_vars.COMPUTE_INSTRUCTION:
                self._memory_store(
                    destination,
                    self._op(
                        self._memory_load(destination, reti),
                        operation,
                        self._memory_load(source, reti),
                    ),
                    reti,
                )
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Instr(operation, [rn.Reg() as destination, rn.Im(val)]) if type(
                operation
            ) in global_vars.COMPUTE_IMMEDIATE_INSTRUCTION:
                self._memory_store(
                    destination,
                    self._op(self._memory_load(destination, reti), operation, int(val)),
                    reti,
                )
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Instr(rn.Load(), [rn.Reg() as destination, rn.Im() as source]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Instr(
                rn.Loadin(),
                [rn.Reg() as reg_source, rn.Reg() as destination, rn.Im(val)],
            ):
                self._memory_store(
                    destination,
                    self._memory_load(
                        self._memory_load(reg_source, reti) + int(val),
                        reti,
                    ),
                    reti,
                )
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Instr(rn.Loadi(), [rn.Reg() as destination, rn.Im(val)]):
                self._memory_store(
                    destination,
                    c_uint32(int(val)).value % 0b1000000_00000000_00000000,
                    reti,
                )
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Instr(rn.Store(), [rn.Reg() as source, rn.Im() as destination]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC")
            case rn.Instr(
                rn.Storein(),
                [rn.Reg() as destination, rn.Reg() as reg_source, rn.Im(val)],
            ):
                self._memory_store(
                    self._memory_load(destination, reti) + int(val),
                    self._memory_load(reg_source, reti),
                    reti,
                )
                reti.reg_increase("PC")
            case rn.Instr(rn.Move(), [rn.Reg() as source, rn.Reg() as destination]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC") if str(
                    destination.reg
                ) != "PC" else reti.do_nothing()
            case rn.Jump(rel, rn.Im(val)):
                match rel:
                    case rn.Lt():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value < 0, int(val), reti
                        )
                    case rn.LtE():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value <= 0, int(val), reti
                        )
                    case rn.Gt():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value > 0, int(val), reti
                        )
                    case rn.GtE():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value >= 0, int(val), reti
                        )
                    case rn.Eq():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value == 0, int(val), reti
                        )
                    case rn.NEq():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value != 0, int(val), reti
                        )
                    case rn.Always():
                        self._jump_condition(True, int(val), reti)
                    case rn.NOp():
                        self._jump_condition(False, int(val), reti)
                    case _:
                        bug_in_interpreter(rel)
            #  case rn.Int(rn.Im(val)):
            #      # save PC to stack
            #      reti.sram_set(reti.reg_get("SP"), c_uint32(reti.reg_get("PC")).value)
            #      reti.reg_set("SP", c_uint32(reti.reg_get("SP")).value - 1)
            #      # jump to start address of isr
            #      reti.reg_set("PC", self._memory_load(int(val) + 2**31, reti))
            #  case rn.Rti():
            #      # restore PC
            #      reti.reg_set(
            #          "PC", reti.sram_get(c_uint32(reti.reg_get("SP")).value + 1)
            #      )
            #      # delete PC from stack
            #      reti.reg_set("SP", c_uint32(reti.reg_get("SP")).value + 1)
            case rn.Call(rn.Name("PRINT"), rn.Reg(reg)):
                if global_vars.args.print:
                    print("Output:\n\t" + str(c_int32(reti.reg_get(str(reg))).value))
                if global_vars.path:
                    if self.first_out:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "w",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(str(c_int32(reti.reg_get(str(reg))).value))
                        self.first_out = False
                    else:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "a",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(" " + str(c_int32(reti.reg_get(str(reg))).value))
                reti.reg_increase("PC")
            case rn.Call(rn.Name("INPUT"), rn.Reg(reg)):
                if self.test_input:
                    reti.reg_set(str(reg), c_uint32(self.test_input.pop()).value)
                else:
                    reti.reg_set(str(reg), c_uint32(int(input())).value)
                reti.reg_increase("PC")
            case _:
                bug_in_interpreter(instr)

    def _instrs(self, reti: RETI):
        while True:
            addr = reti.reg_get("PC")
            if addr > 2**31:
                i = addr - 2**31
                next_instruction = reti.sram_get(i)
            elif addr >= 2**30:
                i = addr - 2**31
                next_instruction = reti.uart_get(i)
            else:  # addr < 2**30
                i = addr
                next_instruction = reti.eprom_get(i)
            match next_instruction:
                case rn.Jump(rn.Always(), rn.Im("0")):
                    self._conclude(reti)
                    break
                case int():
                    self._conclude(reti)
                    break
                case _:
                    reti.save_last_instruction()
                    self._instr(next_instruction, reti)
                    if global_vars.args.intermediate_stages and (
                        global_vars.args.verbose or global_vars.args.double_verbose
                    ):
                        self._reti_state_option(reti)

    def _conclude(self, reti: RETI):
        if global_vars.args.intermediate_stages and not (
            global_vars.args.verbose or global_vars.args.double_verbose
        ):
            self._reti_state_option(reti)
            # in case of an print call as last instruction with the --verbose
            # option, the reti state was already printed
        # needs a newline at the end, else it differs from .out_expected
        file_not_empty = True
        if os.path.isfile(global_vars.path + global_vars.basename + ".out"):
            with open(
                global_vars.path + global_vars.basename + ".out", "r", encoding="utf-8"
            ) as fin:
                file_not_empty = fin.read().replace("\n", "")
        if file_not_empty:
            with open(
                global_vars.path + global_vars.basename + ".out",
                "a",
                encoding="utf-8",
            ) as fout:
                fout.write("\n")
        else:
            with open(
                global_vars.path + global_vars.basename + ".out",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write("\n")

    def _reti_state_option(self, reti_state):
        reti_state.idx.val = str(int(reti_state.idx.val) + 1)
        if global_vars.args.print:
            print(reti_state)
        if global_vars.path:
            if self.first_reti_state:
                with open(
                    global_vars.path + global_vars.basename + ".reti_states",
                    "w",
                    encoding="utf-8",
                ) as fout:
                    fout.write(str(reti_state))
                self.first_reti_state = False
            else:
                with open(
                    global_vars.path + global_vars.basename + ".reti_states",
                    "a",
                    encoding="utf-8",
                ) as fout:
                    fout.write("\n" + str(reti_state))

    def _preconfigs(self, program):
        match program:
            case rn.Program(rn.Name(val)):
                if os.path.isfile(remove_extension(val) + ".in"):
                    with open(
                        remove_extension(val) + ".in", "r", encoding="utf-8"
                    ) as fin:
                        self.test_input = list(
                            reversed(
                                [
                                    int(line)
                                    for line in fin.readline()
                                    .replace("\n", "")
                                    .split(" ")
                                    if line
                                ]
                            )
                        )
            case _:
                bug_in_interpreter(program)

    def interp_reti(self, program: rn.Program):
        match program:
            case rn.Program(_, instrs):
                # filter out comments
                reti = RETI(list(filter_out_comments(instrs)))
            case _:
                bug_in_interpreter(program)
        self._preconfigs(program)
        self._instrs(reti)
