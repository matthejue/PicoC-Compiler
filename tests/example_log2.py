# Author: Jürgen Mattheis, but I've got this algorithm from Thiemann's lecture
# in=128
# golden=7


def log2(a: int) -> int:
    b = -1
    while a > 0:
        b = b + 1
        a = a // 2
    return b


print(log2(input_int()))
