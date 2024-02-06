from reti import RETI
import global_vars
import sys


class Deamon:
    def cont(self, reti: RETI):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        # insert end of file
        print(reti.regs_str())
        while input() != "ack":
            pass
        print(reti.regs_rel_str())
        while input() != "ack":
            pass
        print(reti.eprom_str())
        while input() != "ack":
            pass
        print(reti.uart_str())
        while input() != "ack":
            pass
        print(reti.sram_str())

        while True:
            message = input()
            cmd, args = message.split(" ", 1)
            match cmd:
                case "next":
                    break
                case "set":
                    pass
                case _:
                    pass
