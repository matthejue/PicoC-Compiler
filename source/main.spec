# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


project_root = Path(SPECPATH).parent
if sys.platform == "win32":
    grammar_extension = ".dll"
elif sys.platform == "darwin":
    grammar_extension = ".dylib"
else:
    grammar_extension = ".so"

grammar_libraries = [
    (
        str(project_root / "vendor" / "tree-sitter-picoc" / f"picoc{grammar_extension}"),
        "vendor/tree-sitter-picoc",
    ),
    (
        str(project_root / "vendor" / "tree-sitter-reti" / f"reti{grammar_extension}"),
        "vendor/tree-sitter-reti",
    ),
]

a = Analysis(
    [str(project_root / "source" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=grammar_libraries,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pudb"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="picoc_compiler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
