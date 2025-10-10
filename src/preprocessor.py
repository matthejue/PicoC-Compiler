#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini_pp_fast_enum2.py — One-pass mini preprocessor for #include + header guards.

- Uses enums for both scanner modes (Mode) and include kind (IncludeKind).
- Single scan per file: comment stripping, line splicing, directive handling, emission.
- Supports: #include "..." / <...>, #ifndef/#ifdef/#else/#endif, #define/#undef (existence only), #pragma once.
- Unknown pragmas/directives are preserved (if active).
"""

from __future__ import annotations
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Set, Tuple, Optional

# ---------- Errors & path helpers ----------

class PreprocError(Exception):
    pass

def error(msg: str, file: str, line_no: int) -> None:
    raise PreprocError(f"{file}:{line_no}: {msg}")

def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def current_dir_of(path: str) -> str:
    return os.path.dirname(os.path.abspath(path))

def canonical(path: str) -> str:
    return os.path.realpath(os.path.abspath(path))

# ---------- Enums ----------

class Mode(Enum):
    OUT = auto()
    LINE_COMMENT = auto()
    BLOCK_COMMENT = auto()
    STR = auto()
    CHAR = auto()

class IncludeKind(Enum):
    QUOTED = auto()  # #include "file.h"
    ANGLED = auto()  # #include <file.h>

# ---------- #include helpers ----------

def parse_header_name(rest: str) -> Tuple[IncludeKind, str]:
    """Return (IncludeKind, name). Minimal; no macro expansion."""
    i, n = 0, len(rest)
    while i < n and rest[i].isspace():
        i += 1
    if i >= n:
        raise ValueError("missing header name")
    if rest[i] == '"':
        i += 1
        start = i
        while i < n and rest[i] != '"':
            i += 1
        if i >= n:
            raise ValueError("unterminated header string")
        return (IncludeKind.QUOTED, rest[start:i])
    if rest[i] == '<':
        i += 1
        start = i
        while i < n and rest[i] != '>':
            i += 1
        if i >= n:
            raise ValueError("unterminated header angle name")
        return (IncludeKind.ANGLED, rest[start:i])
    raise ValueError('expected "file" or <file>')

def resolve_include(kind_name: Tuple[IncludeKind, str],
                    include_paths: List[str],
                    curdir: str) -> Optional[str]:
    kind, name = kind_name
    cands: List[str] = []
    if os.path.isabs(name):
        cands = [name]
    else:
        if kind is IncludeKind.QUOTED:
            cands.append(os.path.join(curdir, name))  # current dir first
        for p in include_paths:
            cands.append(os.path.join(p, name))
    for c in cands:
        if os.path.isfile(c):
            return canonical(c)
    return None

# ---------- Conditional state ----------

@dataclass
class CondFrame:
    parent_active: bool
    active: bool
    had_else: bool = False

@dataclass
class PPState:
    defined: Set[str]               # existence-only macro set (for guards)
    once_files: Set[str]            # files seen with #pragma once
    max_depth: int = 200

# ---------- Core: single-pass-ish preprocess ----------

def preprocess(file_path: str,
               include_paths: List[str],
               state: Optional[PPState] = None,
               depth: int = 0) -> str:
    if state is None:
        state = PPState(set(), set())
    if depth > state.max_depth:
        raise PreprocError(f"include recursion depth exceeded at {file_path}")

    file_path = canonical(file_path)
    if file_path in state.once_files:   # #pragma once fast path
        return ""

    s = read(file_path)
    n, i = len(s), 0
    phys_line = 1

    out: List[str] = []
    linebuf: List[str] = []
    cond_stack: List[CondFrame] = []

    mode = Mode.OUT
    at_bol = True  # beginning of logical line

    def is_active() -> bool:
        return (not cond_stack) or cond_stack[-1].active

    while i < n:
        c = s[i]

        # --- line splicing (only in OUT) ---
        if mode is Mode.OUT and c == '\\' and (i + 1 < n) and s[i + 1] in '\n\r':
            if s[i + 1] == '\r' and (i + 2 < n) and s[i + 2] == '\n':
                i += 3
            else:
                i += 2
            phys_line += 1
            continue  # still same logical line

        # --- mode transitions for comments/strings/chars ---
        if mode is Mode.OUT:
            if c == '/':
                if i + 1 < n and s[i + 1] == '/':
                    mode = Mode.LINE_COMMENT; i += 2
                    continue
                if i + 1 < n and s[i + 1] == '*':
                    mode = Mode.BLOCK_COMMENT; i += 2
                    continue
            if c == '"':
                mode = Mode.STR
                if is_active(): linebuf.append(c)
                i += 1; at_bol = False
                continue
            if c == "'":
                mode = Mode.CHAR
                if is_active(): linebuf.append(c)
                i += 1; at_bol = False
                continue

        if mode is Mode.LINE_COMMENT:
            if c == '\n':
                if is_active():
                    linebuf.append(c); out.append(''.join(linebuf))
                linebuf.clear()
                i += 1; phys_line += 1
                mode = Mode.OUT; at_bol = True
            else:
                i += 1
            continue

        if mode is Mode.BLOCK_COMMENT:
            if c == '*' and (i + 1 < n) and s[i + 1] == '/':
                mode = Mode.OUT; i += 2
            else:
                if c == '\n':
                    phys_line += 1
                i += 1
            continue

        if mode is Mode.STR:
            if c == '\\':  # escape
                if is_active(): linebuf.append(c)
                i += 1
                if i < n:
                    if is_active(): linebuf.append(s[i])
                    i += 1
                continue
            if c == '"':
                if is_active(): linebuf.append(c)
                i += 1; mode = Mode.OUT; at_bol = False
                continue
            if is_active(): linebuf.append(c)
            if c == '\n': phys_line += 1; at_bol = True
            i += 1
            continue

        if mode is Mode.CHAR:
            if c == '\\':
                if is_active(): linebuf.append(c)
                i += 1
                if i < n:
                    if is_active(): linebuf.append(s[i])
                    i += 1
                continue
            if c == "'":
                if is_active(): linebuf.append(c)
                i += 1; mode = Mode.OUT; at_bol = False
                continue
            if is_active(): linebuf.append(c)
            if c == '\n': phys_line += 1; at_bol = True
            i += 1
            continue

        # --- regular OUT mode ---
        if at_bol:
            # allow leading whitespace before directives (and preserve it if active)
            if c in ' \t\f\v\r':
                if is_active(): linebuf.append(c)
                i += 1
                continue

            # directive line?
            if c == '#':
                i += 1
                # consume spaces, read keyword
                while i < n and s[i] in ' \t\f\v': i += 1
                kstart = i
                while i < n and (s[i].isalnum() or s[i] == '_'): i += 1
                kw = s[kstart:i]
                while i < n and s[i] in ' \t\f\v': i += 1
                arg_start = i
                while i < n and s[i] != '\n': i += 1
                args = s[arg_start:i].strip()

                # this is a directive: drop any leading whitespace we buffered
                linebuf.clear()

                if kw == 'include':
                    try:
                        kind_name = parse_header_name(args)
                    except ValueError as e:
                        error(f"malformed #include: {e}", file_path, phys_line)
                    inc_path = resolve_include(kind_name, include_paths, current_dir_of(file_path))
                    if inc_path is None:
                        error(f"header not found: {kind_name[1]}", file_path, phys_line)
                    included = preprocess(inc_path, include_paths, state, depth + 1)
                    if is_active(): out.append(included)

                elif kw in ('ifndef', 'ifdef'):
                    # parse identifier
                    j = 0
                    while j < len(args) and args[j].isspace(): j += 1
                    k = j
                    if k >= len(args) or not (args[k] == '_' or args[k].isalpha()):
                        error(f"malformed #{kw} (expected identifier)", file_path, phys_line)
                    while k < len(args) and (args[k] == '_' or args[k].isalnum()): k += 1
                    ident = args[j:k]
                    cond = (ident not in state.defined) if kw == 'ifndef' else (ident in state.defined)
                    parent = is_active()
                    cond_stack.append(CondFrame(parent_active=parent, active=(parent and cond)))

                elif kw == 'else':
                    if not cond_stack:
                        error("#else without opener", file_path, phys_line)
                    frame = cond_stack[-1]
                    if frame.had_else:
                        error("multiple #else in the same conditional block", file_path, phys_line)
                    frame.had_else = True
                    frame.active = frame.parent_active and (not frame.active)

                elif kw == 'endif':
                    if not cond_stack:
                        error("#endif without opener", file_path, phys_line)
                    cond_stack.pop()

                elif kw == 'define':
                    j = 0
                    while j < len(args) and args[j].isspace(): j += 1
                    k = j
                    if k >= len(args) or not (args[k] == '_' or args[k].isalpha()):
                        error("malformed #define (expected identifier)", file_path, phys_line)
                    while k < len(args) and (args[k] == '_' or args[k].isalnum()): k += 1
                    ident = args[j:k]
                    rest = args[k:].strip()
                    if is_active():
                        state.defined.add(ident)
                        # pure guard defines stay internal; macro body is preserved
                        if rest:
                            out.append(f"#define {ident} {rest}\n")

                elif kw == 'undef':
                    j = 0
                    while j < len(args) and args[j].isspace(): j += 1
                    k = j
                    if k >= len(args) or not (args[k] == '_' or args[k].isalpha()):
                        error("malformed #undef (expected identifier)", file_path, phys_line)
                    while k < len(args) and (args[k] == '_' or args[k].isalnum()): k += 1
                    ident = args[j:k]
                    if is_active():
                        state.defined.discard(ident)
                        out.append(f"#undef {ident}\n")

                elif kw == 'pragma':
                    if args.strip() == 'once':
                        state.once_files.add(file_path)  # skip on future includes
                    else:
                        if is_active():
                            out.append(f"#pragma {args}\n")

                else:
                    # Unknown directive: preserve it
                    if is_active():
                        out.append(f"#{kw} {args}\n")

                # consume newline (don’t emit)
                if i < n and s[i] == '\n':
                    i += 1; phys_line += 1; at_bol = True
                continue

            # first non-space at BOL and not '#': normal code
            at_bol = False

        # normal character emission
        if c == '\n':
            if is_active():
                linebuf.append(c); out.append(''.join(linebuf))
            linebuf.clear()
            i += 1; phys_line += 1; at_bol = True
        else:
            if is_active(): linebuf.append(c)
            i += 1

    # flush trailing line
    if linebuf and is_active():
        out.append(''.join(linebuf))

    if cond_stack:
        raise PreprocError(f"{file_path}:{phys_line}: unclosed conditional block (missing #endif)")

    return ''.join(out)

# ---------- Simple CLI ----------

def main(argv: List[str]) -> int:
    import argparse, sys
    ap = argparse.ArgumentParser(description="Fast minimal preprocessor (#include + header guards) with Enums")
    ap.add_argument("input", help="input .c/.h file")
    ap.add_argument("-I", dest="I", action="append", default=[], help="include path (repeatable)")
    ap.add_argument("-D", dest="D", action="append", default=[], help="predefine NAME (for guards)")
    ap.add_argument("--max-depth", type=int, default=200, help="max include depth")
    args = ap.parse_args(argv)

    incs = [canonical(p) for p in (args.I or [])]
    state = PPState(defined=set(args.D or []), once_files=set(), max_depth=args.max_depth)

    try:
        out = preprocess(args.input, incs, state=state)
        sys.stdout.write(out)
        return 0
    except PreprocError as e:
        sys.stderr.write(f"error: {e}\n")
        return 1

if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
