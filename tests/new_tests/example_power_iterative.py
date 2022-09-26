# Author: Jürgen Mattheis, but the algorithm is from Thiemann's lecture
# in=2
# golden=16


def power_iterative(a: int, n: int, acc: int) -> int:
    while n != 0:
        n = n - 1
        acc = acc * a
    return acc


print(power_iterative(input_int(), 4, 1))
