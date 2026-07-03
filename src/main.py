import sys


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        from src.cli_args import build_parser

        build_parser().print_help()
        return

    from src.option_handler import OptionHandler

    compiler = OptionHandler()
    compiler.build_all()
    print("\nCompilation successfull\n")


if __name__ == "__main__":
    main()
