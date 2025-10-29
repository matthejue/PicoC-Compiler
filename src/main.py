import sys
from src.option_handler import OptionHandler, open_documentation
from src. utils.util_funs_dependent import remove_filename, filename_without_ext, remove_ext


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        open_documentation()
        return

    compiler = OptionHandler()
    compiler.build_all()
    print("\nCompilation successfull\n")


if __name__ == "__main__":
    main()
