import sys


def main():
    if set(["-V", "--version"]).intersection(sys.argv):
        from source.build_version import VERSION

        print(f"PicoC-Compiler-{VERSION}")
        return

    if set(["-h", "--help"]).intersection(sys.argv):
        from source.cli_args import build_parser

        build_parser().print_help()
        return

    from source.option_handler import OptionHandler

    compiler = OptionHandler()
    compiler.build_all()
    print("\nCompilation successfull\n")


if __name__ == "__main__":
    main()
