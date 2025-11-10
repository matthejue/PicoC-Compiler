from __future__ import annotations
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set


class PreprocError(Exception):
    pass


class Mode(Enum):
    OUT = auto()
    LINE_COMMENT = auto()
    BLOCK_COMMENT = auto()
    STR = auto()
    CHAR = auto()


class IncludeKind(Enum):
    QUOTED = auto()  # #include "file.h"
    ANGLED = auto()  # #include <file.h>


@dataclass
class _State:
    once_marked: Set[str]
    max_depth: int


class Preprocessor:
    """
    Minimal one-pass preprocessor supporting ONLY:
      - #include "path" / <path>   (exactly one argument; no extras)
      - #pragma once               (skip subsequent includes of that file)

    Resolution rules:
      - "quoted":  search including file's directory, then include_paths, then system_paths
      - <angled>:  search include_paths, then system_paths
      - absolute paths are used as-is

    Notes:
      - `preprocess_file(file_path)` reads from disk and follows includes by path.
      - `preprocess(code, file_path)` lets you pass a source string but still
        resolves includes relative to `file_path`.
      - System include paths are a sensible default; you can override/supplement
        via constructor args.
    """

    def __init__(
        self,
        include_paths: Optional[List[str]] = None,
        system_paths: Optional[List[str]] = None,
        max_depth: int = 200,
    ):
        self.include_paths = [self._canonical(p) for p in (include_paths or [])]
        self.system_paths = (
            [self._canonical(p) for p in system_paths]
            if system_paths is not None
            else self._default_system_include_paths()
        )
        self.state = _State(once_marked=set(), max_depth=max_depth)
        self.macros: dict[str, str] = {}

    # -------- Public API --------

    def reset_once(self) -> None:
        """Clear #pragma once state (useful if reusing the instance)."""
        self.state.once_marked.clear()
        self.macros.clear()

    def preprocess_file(self, file_path: str, depth: int = 0) -> str:
        """Load source from disk and preprocess it (follows #include by filesystem)."""
        code = self._read_file(file_path)
        return self.preprocess(code, file_path, depth)

    def preprocess(self, code: str, file_path: str, depth: int = 0) -> str:
        """Preprocess a source string identified by file_path (for includes & diagnostics)."""
        if depth > self.state.max_depth:
            raise PreprocError(f"include recursion depth exceeded at {file_path}")
        file_path = self._canonical(file_path)

        # Fast-skip if this file was already marked with #pragma once
        if file_path in self.state.once_marked:
            return ""

        s = code
        n, i = len(s), 0
        phys_line = 1

        out: List[str] = []
        linebuf: List[str] = []

        mode = Mode.OUT
        at_bol = True  # beginning of logical line (after line-splicing)

        while i < n:
            c = s[i]

            # Line splicing: "\" + newline keeps same logical line
            if mode is Mode.OUT and c == "\\" and (i + 1 < n) and s[i + 1] in "\n\r":
                if s[i + 1] == "\r" and (i + 2 < n) and s[i + 2] == "\n":
                    i += 3
                else:
                    i += 2
                phys_line += 1
                continue

            # Comment/string/char handling
            if mode is Mode.OUT:
                if c == "/":
                    if i + 1 < n and s[i + 1] == "/":
                        mode = Mode.LINE_COMMENT
                        i += 2
                        continue
                    if i + 1 < n and s[i + 1] == "*":
                        mode = Mode.BLOCK_COMMENT
                        i += 2
                        continue
                if c == '"':
                    mode = Mode.STR
                    linebuf.append(c)
                    i += 1
                    at_bol = False
                    continue
                if c == "'":
                    mode = Mode.CHAR
                    linebuf.append(c)
                    i += 1
                    at_bol = False
                    continue

            if mode is Mode.LINE_COMMENT:
                if c == "\n":
                    linebuf.append(c)
                    out.append("".join(linebuf))
                    linebuf.clear()
                    i += 1
                    phys_line += 1
                    mode = Mode.OUT
                    at_bol = True
                else:
                    i += 1
                continue

            if mode is Mode.BLOCK_COMMENT:
                if c == "*" and (i + 1 < n) and s[i + 1] == "/":
                    mode = Mode.OUT
                    i += 2
                else:
                    if c == "\n":
                        phys_line += 1
                    i += 1
                continue

            if mode is Mode.STR:
                if c == "\\":
                    linebuf.append(c)
                    i += 1
                    if i < n:
                        linebuf.append(s[i])
                        i += 1
                    continue
                if c == '"':
                    linebuf.append(c)
                    i += 1
                    mode = Mode.OUT
                    at_bol = False
                    continue
                linebuf.append(c)
                if c == "\n":
                    phys_line += 1
                    at_bol = True
                i += 1
                continue

            if mode is Mode.CHAR:
                if c == "\\":
                    linebuf.append(c)
                    i += 1
                    if i < n:
                        linebuf.append(s[i])
                        i += 1
                    continue
                if c == "'":
                    linebuf.append(c)
                    i += 1
                    mode = Mode.OUT
                    at_bol = False
                    continue
                linebuf.append(c)
                if c == "\n":
                    phys_line += 1
                    at_bol = True
                i += 1
                continue

            # Detect directives only at beginning-of-line (after optional whitespace)
            if at_bol:
                if c in " \t\f\v\r":
                    linebuf.append(c)
                    i += 1
                    continue

                if c == "#":
                    i += 1
                    # keyword
                    while i < n and s[i] in " \t\f\v":
                        i += 1
                    kstart = i
                    while i < n and (s[i].isalnum() or s[i] == "_"):
                        i += 1
                    kw = s[kstart:i]
                    while i < n and s[i] in " \t\f\v":
                        i += 1
                    # rest of the logical line
                    arg_start = i
                    while i < n and s[i] != "\n":
                        i += 1
                    arg = s[arg_start:i]

                    # directive → drop buffered leading whitespace
                    linebuf.clear()

                    if kw == "include":
                        try:
                            kind, name = self._parse_include_arg(arg)
                        except ValueError as e:
                            self._error(
                                f"malformed #include: {e}", file_path, phys_line
                            )
                        inc_path = self._resolve_include(kind, name, file_path)
                        if inc_path is None:
                            self._error(
                                f"header not found: {name}", file_path, phys_line
                            )
                        # Skip if that header was marked with #pragma once already
                        if inc_path in self.state.once_marked:
                            included = ""
                        else:
                            inc_src = self._read_file(inc_path)
                            included = self.preprocess(inc_src, inc_path, depth + 1)

                        out.append(included)

                    elif kw == "pragma":
                        if arg.strip() == "once":
                            self.state.once_marked.add(file_path)
                        else:
                            out.append(f"#pragma{arg}\n")  # preserve unknown pragmas

                    elif kw == "define":
                        # handle simple object-like macros
                        parts = arg.strip().split(None, 1)
                        if not parts:
                            self._error(
                                "missing macro name in #define", file_path, phys_line
                            )
                        name = parts[0]
                        value = parts[1].strip() if len(parts) > 1 else "1"
                        self.macros[name] = value

                    else:
                        out.append(f"#{kw}{arg}\n")  # preserve unknown directives

                    # consume newline (don’t emit)
                    if i < n and s[i] == "\n":
                        i += 1
                        phys_line += 1
                        at_bol = True
                    continue

                # first non-space, non-# at BOL → normal code
                at_bol = False

            # Normal code — perform macro substitution
            if mode is Mode.OUT and c.isalpha() or c == '_':
                start = i
                while i < n and (s[i].isalnum() or s[i] == '_'):
                    i += 1
                ident = s[start:i]
                if ident in self.macros:
                    linebuf.append(self.macros[ident])
                else:
                    linebuf.append(ident)
                continue

            # Normal character emission
            if c == "\n":
                linebuf.append(c)
                out.append("".join(linebuf))
                linebuf.clear()
                i += 1
                phys_line += 1
                at_bol = True
            else:
                linebuf.append(c)
                i += 1

        # flush trailing line
        if linebuf:
            out.append("".join(linebuf))

        return "".join(out)

    # -------- Helpers --------

    def _parse_include_arg(self, rest: str) -> Tuple[IncludeKind, str]:
        """
        Parse exactly ONE include argument: "path" or <path>.
        Reject extra tokens (strict mode).
        """
        s = rest.strip()
        if not s:
            raise ValueError("missing header name")

        if s[0] == '"':
            i = 1
            start = i
            while i < len(s) and s[i] != '"':
                i += 1
            if i >= len(s):
                raise ValueError('unterminated "..."')
            name = s[start:i]
            tail = s[i + 1 :].strip()
            if tail:
                raise ValueError(f"unexpected extra tokens after header name: {tail!r}")
            return (IncludeKind.QUOTED, name)

        if s[0] == "<":
            i = 1
            start = i
            while i < len(s) and s[i] != ">":
                i += 1
            if i >= len(s):
                raise ValueError("unterminated <...>")
            name = s[start:i]
            tail = s[i + 1 :].strip()
            if tail:
                raise ValueError(f"unexpected extra tokens after header name: {tail!r}")
            return (IncludeKind.ANGLED, name)

        raise ValueError('expected one header name: either "file" or <file>')

    def _resolve_include(
        self, kind: IncludeKind, name: str, including_file: str
    ) -> Optional[str]:
        """Filesystem search for an include according to kind and configured paths."""
        # Absolute path?
        if os.path.isabs(name):
            return self._canonical(name) if os.path.isfile(name) else None

        cands: List[str] = []

        # Quoted: current directory first
        if kind is IncludeKind.QUOTED:
            cands.append(os.path.join(os.path.dirname(including_file), name))

        # Then project include paths
        for p in self.include_paths:
            cands.append(os.path.join(p, name))

        # Then system include paths
        for p in self.system_paths:
            cands.append(os.path.join(p, name))

        for c in cands:
            if os.path.isfile(c):
                return self._canonical(c)
        return None

    @staticmethod
    def _read_file(path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def _canonical(path: str) -> str:
        return os.path.realpath(os.path.abspath(path))

    @staticmethod
    def _default_system_include_paths() -> List[str]:
        """Reasonable defaults for common systems; can be overridden."""
        paths: List[str] = []
        if os.name == "nt":
            # Use INCLUDE env (VS/toolchains set this). It's a ';'-separated list on Windows.
            inc_env = os.environ.get("INCLUDE")
            if inc_env:
                for p in inc_env.split(os.pathsep):
                    if p:
                        paths.append(os.path.normpath(p))
        else:
            # Typical Unix defaults (order matters)
            for p in ("/usr/local/include", "/usr/include"):
                if os.path.isdir(p):
                    paths.append(p)
        return [os.path.realpath(p) for p in paths]

    @staticmethod
    def _error(msg: str, file_path: str, line_no: int) -> None:
        raise PreprocError(f"{file_path}:{line_no}: {msg}")
