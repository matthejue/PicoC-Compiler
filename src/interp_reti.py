from reti_nodes import N
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
            case (N.Add() | N.Addi()):
                return c_int32(c_int32(opd1).value + c_int32(opd2).value).value
            case (N.Sub() | N.Subi()):
                return c_int32(c_int32(opd1).value - c_int32(opd2).value).value
            case (N.Mult() | N.Multi()):
                return c_int32(c_int32(opd1).value * c_int32(opd2).value).value
            case (N.Div() | N.Divi()):
                return c_int32(c_int32(opd1).value // c_int32(opd2).value).value
            case (N.Mod() | N.Modi()):
                return c_int32(c_int32(opd1).value % c_int32(opd2).value).value
            case (N.Oplus() | N.Oplusi()):
                return c_uint32(c_uint32(opd1).value ^ c_uint32(opd2).value).value
            case (N.Or() | N.Ori()):
                return c_uint32(c_uint32(opd1).value | c_uint32(opd2).value).value
            case (N.And() | N.Andi()):
                return c_uint32(c_uint32(opd1).value & c_uint32(opd2).value).value
            case _:
                bug_in_interpreter(op)

    def _memory_store(self, destination, source, reti: RETI) -> int:
        source = c_uint32(source).value
        match destination:
            # addressbus
            case N.Im(val):
                higher_bits = (reti.reg_get("DS") >> 22) % 0b100000000 << 22
                memory_type = reti.reg_get("DS") >> 30
                match memory_type:
                    case 0b00:
                        # error, eprom is readonly
                        reti.eprom_set(abs(int(val)) + higher_bits, source)
                    case 0b01:
                        reti.uart_set(abs(int(val)) + higher_bits, source)
                    case (0b10 | 0b11):
                        reti.sram_set(abs(int(val)) + higher_bits, source)
                    case _:
                        bug_in_interpreter(memory_type)
            case N.Reg(reg):
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
            case N.Im(val):
                higher_bits = (reti.reg_get("DS") >> 22) % 0b100000000 << 22
                memory_type = reti.reg_get("DS") >> 30
                match memory_type:
                    case 0b00:
                        return reti.eprom_get(abs(int(val)) + higher_bits)
                    case 0b01:
                        return reti.uart_get(abs(int(val)) + higher_bits)
                    case (0b10 | 0b11):
                        return reti.sram_get(abs(int(val)) + higher_bits)
                    case _:
                        bug_in_interpreter(memory_type)

            case N.Reg(reg):
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
                bug_in_interpreter(destination)

    def _instr(self, instr, reti: RETI):
        match instr:
            case N.Instr(
                operation,
                [N.Reg() as destination, (N.Im() | N.Reg()) as source],
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
                reti.reg_increase("PC")
            case N.Instr(operation, [N.Reg() as destination, N.Im(val)]) if type(
                operation
            ) in global_vars.COMPUTE_IMMEDIATE_INSTRUCTION:
                self._memory_store(
                    destination,
                    self._op(self._memory_load(destination, reti), operation, int(val)),
                    reti,
                )
                reti.reg_increase("PC")
            case N.Instr(N.Load(), [N.Reg() as destination, N.Im() as source]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC")
            case N.Instr(
                N.Loadin(),
                [N.Reg() as reg_source, N.Reg() as destination, N.Im(val)],
            ):
                self._memory_store(
                    destination,
                    self._memory_load(
                        (abs(self._memory_load(reg_source, reti)) + int(val)) % 2**32,
                        reti,
                    ),
                    reti,
                )
                reti.reg_increase("PC")
            case N.Instr(N.Loadi(), [N.Reg() as destination, N.Im(val)]):
                self._memory_store(
                    destination,
                    int(val),
                    reti,
                )
                reti.reg_increase("PC")
            case N.Instr(N.Store(), [N.Reg() as source, N.Im() as destination]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC")
            case N.Instr(
                N.Storein(),
                [N.Reg() as destination, N.Reg() as reg_source, N.Im(val)],
            ):
                self._memory_store(
                    (abs(self._memory_load(destination, reti)) + int(val)) % 2**32,
                    self._memory_load(reg_source, reti),
                    reti,
                )
                reti.reg_increase("PC")
            case N.Instr(N.Move(), [N.Reg() as source, N.Reg() as destination]):
                self._memory_store(destination, self._memory_load(source, reti), reti)
                reti.reg_increase("PC")
            case N.Jump(rel, N.Im(val)):
                match rel:
                    case N.Lt():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value < 0, int(val), reti
                        )
                    case N.LtE():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value <= 0, int(val), reti
                        )
                    case N.Gt():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value > 0, int(val), reti
                        )
                    case N.GtE():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value >= 0, int(val), reti
                        )
                    case N.Eq():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value == 0, int(val), reti
                        )
                    case N.NEq():
                        self._jump_condition(
                            c_int32(reti.reg_get("ACC")).value != 0, int(val), reti
                        )
                    case N.Always():
                        self._jump_condition(True, int(val), reti)
                    case N.NOp():
                        self._jump_condition(False, int(val), reti)
                    case _:
                        bug_in_interpreter(rel)
            case N.Int(N.Im(val)):
                # save PC to stack
                reti.sram_set(reti.reg_get("SP"), reti.reg_get("PC"))
                reti.reg_set("SP", reti.reg_get("SP") - 1)
                # jump to start address of isr
                reti.reg_set("PC", reti.sram_get(abs(int(val))))
            case N.Rti():
                # restore PC
                reti.reg_set("PC", reti.sram_get(reti.reg_get("SP") + 1))
                # delete PC from stack
                reti.reg_set("SP", reti.reg_get("SP") + 1)
            case N.Call(N.Name("PRINT"), N.Reg(reg)):
                if global_vars.args.print:
                    print("Output:\n\t" + str(reti.reg_get(str(reg))))
                if global_vars.path:
                    if self.first_out:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "w",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(str(reti.reg_get(str(reg))))
                        self.first_out = False
                    else:
                        with open(
                            global_vars.path + global_vars.basename + ".out",
                            "a",
                            encoding="utf-8",
                        ) as fout:
                            fout.write(" " + str(reti.reg_get(str(reg))))
                if (
                    global_vars.args.intermediate_stages
                    and not global_vars.args.verbose
                ):
                    self._reti_state_option(reti)
                reti.reg_increase("PC")
            case N.Call(N.Name("INPUT"), N.Reg(reg)):
                if self.test_input:
                    reti.reg_set(str(reg), self.test_input.pop())
                else:
                    reti.reg_set(str(reg), int(input()))
                reti.reg_increase("PC")
            case _:
                bug_in_interpreter(instr)

    def _instrs(self, program: N.Program, reti: RETI):
        match program:
            case N.Program(_, instrs):
                while True:
                    i = reti.reg_get("PC") - global_vars.args.process_begin - 2**31
                    next_instruction = instrs[i] if i < len(instrs) and i >= 0 else None
                    if not next_instruction:
                        self._conclude(program, reti)
                        break
                        # TODO: raise Errors.JumpedOutOfProgrammError() or LostTrack?
                    match next_instruction:
                        case N.Jump(N.Always(), N.Im("0")):
                            self._conclude(program, reti)
                            break
                        case _:
                            reti.save_last_instruction()
                            self._instr(next_instruction, reti)
                            if (
                                global_vars.args.intermediate_stages
                                and global_vars.args.verbose
                            ):
                                self._reti_state_option(reti)

    def _conclude(self, program, reti):
        if global_vars.args.intermediate_stages and not global_vars.args.verbose:
            match program:
                case N.Program(_, instrs):
                    match instrs[-1]:
                        case N.Call(N.Name("PRINT")):
                            # in case of an print call as last instruction, the
                            # reti state was already printed
                            pass
                        case _:
                            self._reti_state_option(reti)
        # needs a newline at the end, else it differs from .out_expected
        match program:
            case N.Program(N.Name(val)):
                with open(
                    remove_extension(val) + ".out",
                    "a",
                    encoding="utf-8",
                ) as fout:
                    fout.write("\n")
            case _:
                bug_in_interpreter(program)

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

    def _preconfigs(self, program, reti):
        match program:
            case N.Program(N.Name(val), instrs):
                reti.reg_set("CS", global_vars.args.process_begin + 2**31)
                reti.reg_set("PC", global_vars.args.process_begin + 2**31)
                reti.reg_set(
                    "DS",
                    global_vars.args.process_begin + len(instrs) + 2**31,
                )
                reti.reg_set(
                    "SP",
                    global_vars.args.process_begin
                    + len(instrs)
                    + global_vars.args.datasegment_size
                    + 2**31
                    - 1,
                )
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

    def interp_reti(self, program: N.Program):
        match program:
            case N.Program(_, instrs):
                # filter out comments
                program.instrs = list(filter_out_comments(instrs))
                reti = RETI(program.instrs)
            case _:
                bug_in_interpreter(program)
        self._preconfigs(program, reti)
        self._instrs(program, reti)
