#!/usr/bin/env python3

from pathlib import Path
import sys


MODES = {
    "1": {
        "picoc": Path("/home/areo/Documents/Studium/Pico-OS/lib/malloc/malloc.picoc"),
        "header": Path("/home/areo/Documents/Studium/Pico-OS/lib/malloc/malloc.h"),
        "output": Path("/home/areo/Documents/Studium/PicoC-Compiler/sys_tests/include/malloc.h"),
    },
    "2": {
        "picoc": Path("/home/areo/Documents/Studium/Pico-OS/lib/mutex/mutex.picoc"),
        "header": Path("/home/areo/Documents/Studium/Pico-OS/lib/mutex/mutex.h"),
        "output": Path("/home/areo/Documents/Studium/PicoC-Compiler/sys_tests/include/mutex.h"),
    },
    "3": {
        "picoc": Path("/home/areo/Documents/Studium/Pico-OS/lib/stdio/stdio.picoc"),
        "header": Path("/home/areo/Documents/Studium/Pico-OS/lib/stdio/stdio.h"),
        "output": Path("/home/areo/Documents/Studium/PicoC-Compiler/sys_tests/include/stdio.h"),
    },
}

TEST_HEAP_DEFINE = "#define HEAP_SIZE  (5 * 4)     // heap size in words"


def merge_files(picoc_path: Path, header_path: Path, output_path: Path) -> None:
    picoc_text = picoc_path.read_text()
    header_text = header_path.read_text().rstrip("\n")

    include_line = f'#include "{header_path.name}"'
    if include_line not in picoc_text:
        raise ValueError(f'Could not find {include_line!r} in {picoc_path}')

    merged_text = picoc_text.replace(include_line, header_text, 1)
    if output_path.name == "malloc.h":
        merged_text = merged_text.replace(
            "#define HEAP_SIZE  (1024 * 256)     // heap size in words",
            TEST_HEAP_DEFINE,
            1,
        )
    output_path.write_text(merged_text)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "1"
    config = MODES.get(mode)
    if config is None:
        print("usage: merge_lib.py [1|2|3]", file=sys.stderr)
        return 1

    try:
        merge_files(config["picoc"], config["header"], config["output"])
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote merged file to {config['output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
