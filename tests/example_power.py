# Author: Jürgen Mattheis
# in=2
# golden=16


def power(a: int, n: int) -> int:
    if n == 0:
        return 1
    else:
        return a * power(a, n - 1)


print(power(input_int(), 4))
