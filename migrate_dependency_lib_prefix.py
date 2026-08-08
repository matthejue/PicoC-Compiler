#!/usr/bin/env python3
"""Add lib prefixes to PicoC library filenames in sys test dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LIB_FILENAME_RE = re.compile(r"(?<!lib)\b(stdio|string)\.picoc\b")


def rewrite_dependency_line(line: str) -> str:
    stripped = line.lstrip()
    if not stripped.startswith("//") or "dependencies:" not in stripped:
        return line

    return LIB_FILENAME_RE.sub(r"lib\1.picoc", line)


def rewrite_file(path: Path) -> bool:
    original = path.read_text()
    rewritten = "".join(
        rewrite_dependency_line(line)
        for line in original.splitlines(keepends=True)
    )

    if rewritten == original:
        return False

    path.write_text(rewritten)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        "test_dir",
        nargs="?",
        default="test",
        type=Path,
        help="directory containing .picoc system tests",
    )
    args = parser.parse_args()

    changed = [
        path
        for path in sorted(args.test_dir.rglob("*.picoc"))
        if rewrite_file(path)
    ]

    for path in changed:
        print(path)

    print(f"updated {len(changed)} file(s)")


if __name__ == "__main__":
    main()
