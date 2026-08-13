"""
This module is for my math functios
"""


def isPrime(num: int) -> bool:
    """
    Checks if a num is prime.

    Args:
        num: int to be checked

    Returns:
        bool: True if Prime, else False
    """
    i = num - 1
    while i > 1:
        if (num % i) == 0:
            return True
        i -= 1
    return False


def factorial(num: int) -> int:
    """
        Calculate factorial of given number.

    Args:
        num: int, the number to calculate factorial for.

    Returns:
        Facotiral of given number.
    """
    if num == 0:
        return 1
    if num == 1:
        return 1

    return num * factorial(num - 1)
