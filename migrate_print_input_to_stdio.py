#!/usr/bin/env python3
"""Rewrite old PicoC print/input builtins to stdio printf/scanf calls."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_STDIO_PICOC = "/home/areo/Documents/Studium/Pico-OS/lib/stdio/stdio.picoc"
DEFAULT_STDIO_HEADER = "/home/areo/Documents/Studium/Pico-OS/lib/stdio/stdio.header"


def is_ident_start(ch: str) -> bool:
    return ch == "_" or ch.isalpha()


def is_ident_part(ch: str) -> bool:
    return ch == "_" or ch.isalnum()


def previous_significant(text: str) -> str | None:
    for ch in reversed(text):
        if not ch.isspace():
            return ch
    return None


def looks_like_expression_call(prefix: str) -> bool:
    prev = previous_significant(prefix)
    return prev is None or prev in "=({[,?:+-*/%!<>;&|^"


def parse_empty_call(line: str, pos: int) -> int | None:
    i = pos
    while i < len(line) and line[i].isspace():
        i += 1
    if i >= len(line) or line[i] != "(":
        return None
    i += 1
    while i < len(line) and line[i].isspace():
        i += 1
    if i >= len(line) or line[i] != ")":
        return None
    return i + 1


def indentation(line: str) -> str:
    return line[: len(line) - len(line.lstrip(" \t"))]


def rewrite_line(line: str, in_block_comment: bool, next_tmp: int):
    out = []
    prefixes = []
    i = 0
    state = "block_comment" if in_block_comment else "normal"

    while i < len(line):
        ch = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ""

        if state == "block_comment":
            out.append(ch)
            if ch == "*" and nxt == "/":
                out.append(nxt)
                i += 2
                state = "normal"
                continue
            i += 1
            continue

        if state == "string":
            out.append(ch)
            if ch == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                state = "normal"
            i += 1
            continue

        if state == "char":
            out.append(ch)
            if ch == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if ch == "'":
                state = "normal"
            i += 1
            continue

        if ch == "/" and nxt == "/":
            out.append(line[i:])
            i = len(line)
            continue
        if ch == "/" and nxt == "*":
            out.append(ch)
            out.append(nxt)
            i += 2
            state = "block_comment"
            continue
        if ch == '"':
            out.append(ch)
            state = "string"
            i += 1
            continue
        if ch == "'":
            out.append(ch)
            state = "char"
            i += 1
            continue

        if is_ident_start(ch):
            start = i
            i += 1
            while i < len(line) and is_ident_part(line[i]):
                i += 1
            ident = line[start:i]
            prefix = "".join(out)

            if ident == "print" and looks_like_expression_call(prefix):
                j = i
                while j < len(line) and line[j].isspace():
                    j += 1
                if j < len(line) and line[j] == "(":
                    out.append("printf")
                    out.append(line[i : j + 1])
                    out.append('"%d ", ')
                    i = j + 1
                    continue

            if ident == "input" and looks_like_expression_call(prefix):
                end = parse_empty_call(line, i)
                if end is not None:
                    tmp = f"__picoc_input_{next_tmp}"
                    next_tmp += 1
                    indent = indentation(line)
                    prefixes.append(
                        f"{indent}int {tmp};\n"
                        f'{indent}scanf("%d ", &{tmp});\n'
                    )
                    out.append(tmp)
                    i = end
                    continue

            out.append(ident)
            continue

        out.append(ch)
        i += 1

    return "".join(prefixes) + "".join(out), state == "block_comment", next_tmp


def line_has_dependency(line: str, dependency: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("//") and "dependencies:" in stripped and dependency in stripped


def line_is_dependency(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("//") and "dependencies:" in stripped


def add_metadata(code: str, dependency: str, header: str) -> str:
    lines = code.splitlines(keepends=True)
    include_line = f'#include "{header}"\n'
    dependency_line = f"// dependencies: {dependency}\n"

    has_include = any(line.strip() == include_line.strip() for line in lines)
    has_dependency = any(line_has_dependency(line, dependency) for line in lines)

    if not has_dependency:
        for idx, line in enumerate(lines):
            if line_is_dependency(line):
                line_ending = "\n" if line.endswith("\n") else ""
                lines[idx] = line.rstrip("\n") + f" {dependency}" + line_ending
                break
        else:
            insert_at = 0
            for idx, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("//") or stripped == "":
                    insert_at = idx + 1
                    continue
                break
            lines.insert(insert_at, dependency_line)

    if not has_include:
        insert_at = 0
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("//") or stripped == "":
                insert_at = idx + 1
                continue
            break
        lines.insert(insert_at, include_line)

    return "".join(lines)


def rewrite_code(code: str, dependency: str, header: str) -> str:
    in_block_comment = False
    next_tmp = 0
    out_lines = []

    for line in code.splitlines(keepends=True):
        rewritten, in_block_comment, next_tmp = rewrite_line(
            line, in_block_comment, next_tmp
        )
        out_lines.append(rewritten)

    rewritten = "".join(out_lines)
    if rewritten == code:
        return code
    return add_metadata(rewritten, dependency, header)


def iter_picoc_files(paths):
    for path_arg in paths:
        path = Path(path_arg)
        if path.is_dir():
            yield from sorted(path.rglob("*.picoc"))
        else:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace old PicoC print()/input() usage with stdio printf()/scanf()."
    )
    parser.add_argument("paths", nargs="+", help="PicoC files or directories to rewrite")
    parser.add_argument("--stdio-picoc", default=DEFAULT_STDIO_PICOC)
    parser.add_argument("--stdio-header", default=DEFAULT_STDIO_HEADER)
    parser.add_argument("--dry-run", action="store_true", help="print files that would change")
    args = parser.parse_args()

    changed = []
    for path in iter_picoc_files(args.paths):
        code = path.read_text(encoding="utf-8")
        rewritten = rewrite_code(code, args.stdio_picoc, args.stdio_header)
        if rewritten == code:
            continue
        changed.append(path)
        if not args.dry_run:
            path.write_text(rewritten, encoding="utf-8")

    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
