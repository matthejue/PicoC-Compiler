#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys


def heading(heading, terminal_width, symbol):
    print(
        _strip_multiline_string(
            f"""\033[1;37m{symbol * terminal_width}
    {symbol + ' ' + ' ' * ((terminal_width - len(heading) - 6) // 2 +
    (1 if (terminal_width - len(heading) - 4) % 2 else 0))}{heading}{' ' *
    ((terminal_width - len(heading) - 4) // 2) + ' ' + symbol}
    {symbol * terminal_width}\033[0;0m"""
        )
    )


def subheading(heading, terminal_width, symbol):
    print(
        f"{symbol * ((terminal_width - len(heading) - 2) // 2 + (1 if (terminal_width - len(heading)) % 2 else 0))} {heading} {symbol * ((terminal_width - len(heading) - 2) // 2)}"
    )


def _strip_multiline_string(multiline_str):
    """helper function to make mutlineline string usable on different
    indent levels

    :grammar: grammar specification
    :returns: None
    """
    lines = multiline_str.split("\n")
    multiline_str = "".join([line.lstrip() + "\n" for line in lines[:-1]])
    multiline_str += lines[-1].lstrip()
    # every code piece ends with \n, so the last element can always be poped
    return multiline_str


if __name__ == "__main__":
    if sys.argv[1] == "subheading":
        subheading(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "heading":
        heading(sys.argv[2], int(sys.argv[3]), sys.argv[4])
