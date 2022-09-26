# Author Jürgen Mattheis, but the algorithm is from Prof. Basts lecture
# in=
# golden=12345


def min_sort(arr: list[int]) -> list[int]:
    arr_len = len(arr)
    i = 0
    while i < arr_len:
        minimum = arr[i]
        minimum_index = i
        j = i + 1
        while j < arr_len:
            if arr[j] < minimum:
                minimum = arr[j]
                minimum_index = j
            j = j + 1
        tmp = arr[i]
        arr[i] = arr[minimum_index]
        arr[minimum_index] = tmp
        i = i + 1
    return arr


a = min_sort([2, 1, 5, 3, 4])
print(a[0])
print(a[1])
print(a[2])
print(a[3])
print(a[4])
