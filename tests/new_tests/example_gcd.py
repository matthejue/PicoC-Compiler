# Author: Jürgen Mattheis
# in=12
# in=9
# golden=3


def gcd(a: int, b: int) -> int:
    while b != 0:
        c = a % b
        a = b
        b = c
    return a


print(gcd(input_int(), input_int()))
