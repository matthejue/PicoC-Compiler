from reti import RETI
import global_vars


def _write_to_pipe(pipe_name, content):
    pipe_path = "/tmp/reti-debugger/" + pipe_name
    try:
        with open(pipe_path, "w") as pipe:
            pipe.write(content)
    except FileNotFoundError:
        print("The RETI-Debugger Neovim Plugin is not running")
        exit(1)


def _read_next_command():
    pipe_path = "/tmp/reti-debugger/command"
    try:
        with open(pipe_path, "r") as pipe:
            return pipe.read()
    except FileNotFoundError:
        print("The RETI-Debugger Neovim Plugin is not running")
        exit(1)


class Deamon:
    def cont(self, reti: RETI):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        _write_to_pipe("registers", reti.regs_str())
        _write_to_pipe("registers_rel", reti.regs_rel_str())
        _write_to_pipe("eprom", reti.eprom_str())
        _write_to_pipe("uart", reti.uart_str())
        _write_to_pipe("sram", reti.sram_str())

        while True:
            command = _read_next_command()
            match command:
                case "next":
                    break
                case _:
                    pass
