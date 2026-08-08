#!/usr/bin/env python3

import argparse
import platform
import shlex
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELEASE_SUPPORT = PROJECT_ROOT / ".github" / "release" / "android"
PYTHON_VERSION = "3.14"
ARCHITECTURES = {
    "aarch64": "aarch64-linux-android",
    "x86_64": "x86_64-linux-android",
}
GRAMMARS = (
    ("tree-sitter-picoc", "picoc.so"),
    ("tree-sitter-reti", "reti.so"),
)
BINDING_SOURCES = (
    "tree_sitter/core/lib/src/lib.c",
    "tree_sitter/binding/language.c",
    "tree_sitter/binding/lookahead_iterator.c",
    "tree_sitter/binding/node.c",
    "tree_sitter/binding/parser.c",
    "tree_sitter/binding/query.c",
    "tree_sitter/binding/query_cursor.c",
    "tree_sitter/binding/query_predicates.c",
    "tree_sitter/binding/range.c",
    "tree_sitter/binding/tree.c",
    "tree_sitter/binding/tree_cursor.c",
    "tree_sitter/binding/module.c",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a self-contained PicoC Compiler package for Termux"
    )
    parser.add_argument("--ndk", type=Path, required=True)
    parser.add_argument("--arch", choices=ARCHITECTURES, default="aarch64")
    parser.add_argument("--api", type=int, default=24)
    parser.add_argument("--python-runtime", type=Path, required=True)
    parser.add_argument("--tree-sitter-source", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("binary/picoc-compiler-android-arm64.tar.gz"),
    )
    return parser.parse_args()


def copy_source(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def extract(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as source:
        source.extractall(destination)


def run(command: list[str]) -> None:
    print(shlex.join(command), flush=True)
    subprocess.run(command, check=True)


def toolchain_directory(ndk: Path) -> Path:
    host = platform.system().lower()
    machine = platform.machine().lower()
    if host == "linux":
        directory = "linux-x86_64"
    elif host == "darwin" and machine in {"arm64", "aarch64"}:
        directory = "darwin-arm64"
    elif host == "darwin":
        directory = "darwin-x86_64"
    else:
        raise SystemExit(f"unsupported Android NDK host: {host}-{machine}")
    return ndk.resolve() / "toolchains" / "llvm" / "prebuilt" / directory


def find_tree_sitter_root(extracted_root: Path) -> Path:
    candidates = list(extracted_root.glob("tree-sitter-*"))
    for candidate in candidates:
        if (candidate / "tree_sitter" / "binding" / "module.c").is_file():
            return candidate
    raise SystemExit("Tree-sitter source archive has an unexpected layout")


def compile_grammar(cc: Path, grammar_name: str, output: Path) -> None:
    grammar_root = PROJECT_ROOT / "vendor" / grammar_name
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            str(cc),
            "-shared",
            "-fPIC",
            "-O2",
            f"-I{grammar_root / 'src'}",
            str(grammar_root / "src" / "parser.c"),
            "-o",
            str(output),
        ]
    )


def compile_tree_sitter_binding(
    cc: Path, source_root: Path, python_prefix: Path, output: Path
) -> None:
    binding_root = source_root / "tree_sitter"
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            str(cc),
            "-shared",
            "-fPIC",
            "-O2",
            "-std=c11",
            "-fvisibility=hidden",
            "-Wno-cast-function-type",
            "-Werror=implicit-function-declaration",
            "-D_POSIX_C_SOURCE=200112L",
            "-D_DEFAULT_SOURCE",
            "-DPY_SSIZE_T_CLEAN",
            "-DTREE_SITTER_HIDE_SYMBOLS",
            f"-I{binding_root / 'binding'}",
            f"-I{binding_root / 'core' / 'lib' / 'include'}",
            f"-I{binding_root / 'core' / 'lib' / 'src'}",
            f"-I{python_prefix / 'include' / f'python{PYTHON_VERSION}'}",
            *[str(source_root / source) for source in BINDING_SOURCES],
            f"-L{python_prefix / 'lib'}",
            f"-lpython{PYTHON_VERSION}",
            "-Wl,--no-undefined",
            "-o",
            str(output),
        ]
    )


def compile_launcher(cc: Path, python_prefix: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            str(cc),
            "-O2",
            "-fPIE",
            "-pie",
            f"-I{python_prefix / 'include' / f'python{PYTHON_VERSION}'}",
            str(RELEASE_SUPPORT / "picoc_compiler.c"),
            f"-L{python_prefix / 'lib'}",
            f"-lpython{PYTHON_VERSION}",
            "-ldl",
            "-lm",
            "-Wl,--no-undefined",
            "-o",
            str(output),
        ]
    )


def create_package(args: argparse.Namespace) -> Path:
    python_archive = args.python_runtime.resolve()
    tree_sitter_archive = args.tree_sitter_source.resolve()
    if not python_archive.is_file() or not tree_sitter_archive.is_file():
        raise SystemExit("Android Python or Tree-sitter source archive is missing")

    toolchain = toolchain_directory(args.ndk)
    target = ARCHITECTURES[args.arch]
    cc = toolchain / "bin" / f"{target}{args.api}-clang"
    if not cc.is_file():
        raise SystemExit(f"Android compiler not found: {cc}")

    stage_root = PROJECT_ROOT / "binary" / f"android-{args.arch}"
    package_root = stage_root / "picoc-compiler"
    shutil.rmtree(stage_root, ignore_errors=True)
    package_root.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="picoc-android-") as temporary:
        extracted_root = Path(temporary)
        python_root = extracted_root / "python"
        tree_sitter_root = extracted_root / "tree-sitter"
        python_root.mkdir()
        tree_sitter_root.mkdir()
        extract(python_archive, python_root)
        extract(tree_sitter_archive, tree_sitter_root)

        python_prefix = python_root / "prefix"
        if not (python_prefix / "lib" / f"libpython{PYTHON_VERSION}.so").is_file():
            raise SystemExit("Android Python archive has an unexpected layout")
        binding_source = find_tree_sitter_root(tree_sitter_root)

        copy_source(PROJECT_ROOT / "source", package_root / "app" / "source")
        shutil.copytree(
            python_prefix / "lib",
            package_root / "runtime" / "lib",
            symlinks=True,
        )

        tree_sitter_package = package_root / "lib" / "python" / "tree_sitter"
        tree_sitter_package.mkdir(parents=True)
        for source in ("__init__.py", "__init__.pyi", "py.typed"):
            shutil.copy2(binding_source / "tree_sitter" / source, tree_sitter_package)
        compile_tree_sitter_binding(
            cc,
            binding_source,
            python_prefix,
            tree_sitter_package / f"_binding.cpython-314-{target}.so",
        )

        for grammar_name, library_name in GRAMMARS:
            compile_grammar(
                cc,
                grammar_name,
                package_root / "app" / "vendor" / grammar_name / library_name,
            )

        compile_launcher(
            cc, python_prefix, package_root / "libexec" / "picoc_compiler"
        )

        license_root = package_root / "LICENSES"
        license_root.mkdir()
        shutil.copy2(PROJECT_ROOT / "LICENSE", license_root / "PicoC-Compiler.txt")
        shutil.copy2(binding_source / "LICENSE", license_root / "Tree-sitter.txt")
        shutil.copy2(
            python_prefix / "lib" / f"python{PYTHON_VERSION}" / "LICENSE.txt",
            license_root / "Python.txt",
        )

    shutil.copy2(RELEASE_SUPPORT / "picoc_compiler", package_root / "picoc_compiler")
    shutil.copy2(RELEASE_SUPPORT / "README.md", package_root / "README.md")
    for executable in (
        package_root / "picoc_compiler",
        package_root / "libexec" / "picoc_compiler",
    ):
        executable.chmod(0o755)

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        archive.add(package_root, arcname=package_root.name)
    return output


def main() -> None:
    output = create_package(parse_args())
    print(output)


if __name__ == "__main__":
    main()
