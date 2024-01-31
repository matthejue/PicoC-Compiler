from reti import RETI
import os


def _write_to_pipe(pipe_name, content):
    pipe_path = "/tmp/" + pipe_name
    with open(pipe_path, "w") as pipe:
        pipe.write(content)


def _read_next_command():
    pipe_path = "/tmp/command"
    with open(pipe_path, "r") as pipe:
        return pipe.read()


class Deamon:
    def create_pipes(self):
        os.mkfifo("/tmp/registers")
        os.mkfifo("/tmp/eprom")
        os.mkfifo("/tmp/uart")
        os.mkfifo("/tmp/sram")

    def remove_pipes(self):
        os.unlink("/tmp/registers")
        os.unlink("/tmp/eprom")
        os.unlink("/tmp/uart")
        os.unlink("/tmp/sram")

    def cont(self, reti: RETI):
        _write_to_pipe("registers", reti.print_regs())
        _write_to_pipe("eprom", reti.print_eprom())
        _write_to_pipe("uart", reti.print_uart())
        _write_to_pipe("sram", reti.print_sram())

        while True:
            command = _read_next_command()
            match command:
                case "next":
                    break
                case _:
                    pass
