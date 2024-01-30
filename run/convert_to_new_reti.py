#!/usr/bin/env python
from sys import argv


def main():
    with open(argv[1], "r") as fin:
        lines = []
        for line in fin.readlines():
            line = line.upper()
            if "LOAD " in line:
                num = line.split(" ")[-1]
                lines += [f"LOAD ACC {num}"]
            elif "STORE " in line:
                num = line.split(" ")[-1]
                lines += [f"STORE ACC {num}"]
            elif "SUB " in line:
                num = line.split(" ")[-1]
                lines += [f"SUB ACC {num}"]
            elif "ADD " in line:
                num = line.split(" ")[-1]
                lines += [f"ADD ACC {num}"]
            elif "JUMP= " in line:
                num = line.split(" ")[-1]
                lines += [f"JUMP== {num}"]
            else:
                lines += [line]
    with open(argv[1], "w") as fout:
        fout.writelines(lines)


if __name__ == "__main__":
    main()
