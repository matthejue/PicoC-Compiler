# Author: Jürgen Mattheis, but the algorithm is from Thiemann's lecture
# in=2
# golden=128


def fast_efficient_iterative(a: int, n: int, acc: int) -> int:
    while n != 0:
        if n % 2 == 0:
            a = a * a
            n = n // 2
        else:
            tmp = a
            a = a * a
            n = n // 2
            acc = acc * tmp
    return acc


print(fast_efficient_iterative(input_int(), 7, 1))
