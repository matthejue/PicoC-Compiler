#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAMMARS = (
    ("tree-sitter-picoc", "picoc"),
    ("tree-sitter-reti", "reti"),
)


def library_extension() -> str:
    if sys.platform == "win32":
        return ".dll"
    if sys.platform == "darwin":
        return ".dylib"
    return ".so"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the vendored Tree-sitter grammar libraries"
    )
    parser.add_argument(
        "grammars",
        nargs="*",
        help="Grammar directories to build; defaults to every grammar",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Write libraries below this root instead of into vendor",
    )
    return parser.parse_args()


def split_compiler_command(compiler: str, platform_name: str) -> list[str]:
    if platform_name == "win32":
        return [compiler]
    return shlex.split(compiler)


def main() -> None:
    args = parse_args()
    selected_grammars = set(args.grammars)
    known_grammars = {directory_name for directory_name, _ in GRAMMARS}
    unknown_grammars = selected_grammars - known_grammars
    if unknown_grammars:
        raise SystemExit(f"unknown grammar: {', '.join(sorted(unknown_grammars))}")

    compiler_value = os.environ.get("CC", "cc")
    compiler = split_compiler_command(compiler_value, sys.platform)
    for directory_name, library_stem in GRAMMARS:
        if selected_grammars and directory_name not in selected_grammars:
            continue
        grammar_dir = PROJECT_ROOT / "vendor" / directory_name
        parser_path = grammar_dir / "src" / "parser.c"
        if args.output_root is None:
            output_path = grammar_dir / f"{library_stem}{library_extension()}"
        else:
            output_path = (
                args.output_root
                / "vendor"
                / directory_name
                / f"{library_stem}{library_extension()}"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [*compiler, "-shared", "-O2"]
        if sys.platform != "win32":
            command.append("-fPIC")
        command.extend(
            [
                f"-I{grammar_dir / 'src'}",
                str(parser_path),
                "-o",
                str(output_path),
            ]
        )
        print(" ".join(shlex.quote(part) for part in command), flush=True)
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
