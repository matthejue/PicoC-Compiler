#!/usr/bin/env python3

from pathlib import Path
import sys


DEFAULT_PICOC = Path("/home/areo/Documents/Studium/Pico-OS/lib/malloc/simple_malloc.picoc")
DEFAULT_HEADER = Path("/home/areo/Documents/Studium/Pico-OS/lib/malloc/simple_malloc.h")
DEFAULT_OUTPUT = Path("/home/areo/Documents/Studium/PicoC-Compiler/sys_tests/include/simple_malloc.h")


def merge_files(picoc_path: Path, header_path: Path, output_path: Path) -> None:
    picoc_text = picoc_path.read_text()
    header_text = header_path.read_text().rstrip("\n")

    include_line = f'#include "{header_path.name}"'
    if include_line not in picoc_text:
        raise ValueError(f'Could not find {include_line!r} in {picoc_path}')

    merged_text = picoc_text.replace(include_line, header_text, 1)
    output_path.write_text(merged_text)


def main() -> int:
    try:
        merge_files(DEFAULT_PICOC, DEFAULT_HEADER, DEFAULT_OUTPUT)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote merged file to {DEFAULT_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
