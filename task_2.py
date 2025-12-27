from typing import List, Tuple, Optional


def binary_search_upper_bound(arr: List[float], target: float) -> Tuple[int, Optional[float]]:
    """
    Повертає кортеж:
    (кількість ітерацій, upper_bound)

    upper_bound = найменший елемент масиву, який >= target
    Якщо такого елемента немає (target більший за всі), upper_bound = None
    """
    left, right = 0, len(arr) - 1
    iterations = 0
    upper_bound = None

    while left <= right:
        iterations += 1
        mid = (left + right) // 2

        if arr[mid] >= target:
            upper_bound = arr[mid]
            right = mid - 1
        else:
            left = mid + 1

    return iterations, upper_bound


if __name__ == "__main__":
    data = [0.5, 1.2, 2.3, 3.3, 4.4, 10.1]
    tests = [0.1, 1.2, 1.21, 3.0, 10.1, 99.9]

    for t in tests:
        iters, ub = binary_search_upper_bound(data, t)
        print(f"target={t} -> iterations={iters}, upper_bound={ub}")
