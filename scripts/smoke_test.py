#!/usr/bin/env python3

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SMOKE_SOURCE = PROJECT_ROOT / "test" / "basic_assembly_instr.picoc"


def main() -> None:
    if len(sys.argv) > 2:
        raise SystemExit("usage: smoke_test.py [compiler]")

    if len(sys.argv) == 2:
        compiler = [str(Path(sys.argv[1]).resolve())]
    else:
        compiler = [sys.executable, str(PROJECT_ROOT / "run.py")]

    with tempfile.TemporaryDirectory(prefix="picoc-smoke-") as temp_dir:
        temp_path = Path(temp_dir)
        source_path = temp_path / "smoke.picoc"
        output_path = temp_path / "smoke.reti"
        shutil.copy2(SMOKE_SOURCE, source_path)
        subprocess.run(
            [
                *compiler,
                "--direct-source-link",
                str(source_path),
                "-o",
                str(output_path),
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )
        if output_path.stat().st_size == 0:
            raise SystemExit("compiler produced an empty RETI file")


if __name__ == "__main__":
    main()
