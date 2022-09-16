# Author: Jürgen Mattheis, but actually Prof. Thiemann, because I've got this
# algorithm from his "Einführung in die Programmierung" lecture ^_^
# in: 2
# golden: 128


def power_efficient(a: int, n: int) -> int:
    if n == 0:
        return 1
    elif n % 2 == 0:
        return power_efficient(a * a, n // 2)
    else:
        return a * power_efficient(a * a, n // 2)


print(power_efficient(input_int(), 7))
