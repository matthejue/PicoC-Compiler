import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        prog="picoc-compiler",
        description="Compile PicoC source files or link RETI block files.",
    )
    parser.add_argument(
        "infiles",
        nargs="+",
        metavar="FILE",
        help="Input .picoc, .reti_blocks, or matching .st file",
    )
    parser.add_argument(
        "-i",
        "--intermediate_stages",
        action="store_true",
        help="Print intermediate compiler stages",
    )
    parser.add_argument(
        "-w",
        "--write_files",
        dest="write_files",
        action="store_true",
        help="Write intermediate stages to side files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Add comments and print parsed CLI options",
    )
    parser.add_argument(
        "-vv",
        "--double_verbose",
        action="store_true",
        help="Show wider parse trees and extra AST/type details",
    )
    parser.add_argument(
        "-t",
        "--testmode",
        action="store_true",
        help="Read test metadata from <input>.input and <input>.expected_output",
    )
    parser.add_argument(
        "-T",
        "--traceback",
        action="store_true",
        help="Show full tracebacks on errors",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "-s",
        "--supress_errors",
        action="store_true",
        help="Skip the external C syntax check",
    )
    parser.add_argument(
        "-b", "--binary", action="store_true", help="Produce binary output"
    )
    parser.add_argument(
        "-m",
        "--metadata_comments",
        action="store_true",
        help="Copy top-of-file input/expected/datasegment comments into final .reti",
    )
    parser.add_argument(
        "-I",
        "--include",
        dest="I",
        metavar="PATH",
        action="append",
        default=[],
        help="Add an include path (can be used multiple times)",
    )
    parser.add_argument(
        "-M",
        "--max-depth",
        metavar="DEPTH",
        type=int,
        default=200,
        help="Maximum include depth (default: 200)",
    )
    parser.add_argument(
        "-o",
        "--output_name",
        metavar="OUTPUT",
        type=str,
        default="a.reti",
        help=(
            "Name of the linked RETI output file, or the path used for "
            "memory_constants.header with -k (default: a.reti)"
        ),
    )
    parser.add_argument(
        "-c",
        "--compile",
        action="store_true",
        help="Compile source files without linking (like gcc -c)",
    )
    parser.add_argument(
        "-C",
        "--startup-source",
        metavar="PATH",
        help=(
            "Link an additional PicoC startup source; if it defines _start, "
            "that function replaces the generated default _start"
        ),
    )
    parser.add_argument(
        "-g",
        "--generate_debuginfo",
        action="store_true",
        help="Write <output>.debuginfo for linked '.picoc' inputs",
    )
    parser.add_argument(
        "-k",
        "--kernelheader",
        choices=("sram", "eprom"),
        metavar="{sram,eprom}",
        help=(
            "Write only memory_constants.header for an SRAM or EPROM program; "
            "-o chooses the header path, not a .reti output path"
        ),
    )
    parser.add_argument(
        "-O0",
        dest="optimization_level",
        action="store_const",
        const=0,
        default=0,
        help="Disable optimizations (default)",
    )
    parser.add_argument(
        "-O1",
        dest="optimization_level",
        action="store_const",
        const=1,
        help="Enable compile-time global initializer data generation",
    )
    return parser
