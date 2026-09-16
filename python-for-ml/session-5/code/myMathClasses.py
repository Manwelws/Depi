"""
This module wraps the math functions from myMath in classes.
"""


class IsPrime:
    """
    Checks whether a number is prime.
    """

    @staticmethod
    def check(num: int) -> bool:
        """
        Checks if a num is prime.

        Args:
            num: int to be checked

        Returns:
            bool: True if Prime, else False
        """
        if num < 2:
            return False
        i = 2
        while i * i <= num:
            if (num % i) == 0:
                return False
            i += 1
        return True


class Factorial:
    """
    Calculates the factorial of a number.
    """

    @staticmethod
    def calculate(num: int) -> int:
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

        return num * Factorial.calculate(num - 1)


class MultiplicationTable:
    """
    Prints the multiplication table of a number.
    """

    @staticmethod
    def print_table(num: int) -> None:
        """
        Prints the multiplication table of the given number from 1 to 10.

        Args:
            num: int, the number to print its multiplication table.
        """
        for i in range(1, 11):
            print(f"{num} x {i} = {num * i}")


class TwinPrimes:
    """
    Prints all twin primes below a given limit.
    """

    @staticmethod
    def print_twins(limit: int = 1000) -> None:
        """
        Prints all twin primes less than the given limit.

        Twin primes are pairs of consecutive odd numbers that are both prime.

        Args:
            limit: int, upper bound (exclusive). Defaults to 1000.
        """
        for num in range(3, limit - 1):
            if IsPrime.check(num) and IsPrime.check(num + 2):
                print(f"({num}, {num + 2})")


class PrimeFactors:
    """
    Finds the prime factors of a number.
    """

    @staticmethod
    def find(num: int) -> list:
        """
        Finds the prime factors of a number.

        Example: prime factors of 56 are [2, 2, 2, 7]

        Args:
            num: int, the number to factorize.

        Returns:
            list: the prime factors of the given number.
        """
        factors = []
        divisor = 2
        while divisor * divisor <= num:
            while num % divisor == 0:
                factors.append(divisor)
                num //= divisor
            divisor += 1
        if num > 1:
            factors.append(num)
        return factors


class DecimalToBinary:
    """
    Converts a decimal number to its binary representation.
    """

    @staticmethod
    def convert(num: int) -> str:
        """
        Converts a decimal number to its binary representation.

        Args:
            num: int, the decimal number to convert.

        Returns:
            str: the binary representation of the number.
        """
        if num == 0:
            return "0"
        binary = ""
        while num > 0:
            binary = str(num % 2) + binary
            num //= 2
        return binary


class ProperDivisorsSum:
    """
    Computes the sum of the proper divisors of a number.
    """

    @staticmethod
    def compute(num: int) -> int:
        """
        Computes the sum of the proper divisors of a number.

        Args:
            num: int, the number whose proper divisors are summed.

        Returns:
            int: the sum of the proper divisors of the number.
        """
        total = 0
        for i in range(1, num):
            if num % i == 0:
                total += i
        return total


class IsPerfect:
    """
    Checks whether a number is perfect.
    """

    @staticmethod
    def check(num: int) -> bool:
        """
        Checks if a number is perfect.

        A number is perfect if the sum of its proper divisors equals the
        number itself. Example: 28 is perfect since 1+2+4+7+14=28.

        Args:
            num: int, the number to check.

        Returns:
            bool: True if the number is perfect, else False.
        """
        return ProperDivisorsSum.compute(num) == num


class PerfectNumbers:
    """
    Prints all the perfect numbers in a given range.
    """

    @staticmethod
    def print_in_range(start: int, end: int) -> None:
        """
        Prints all the perfect numbers in the given range (inclusive).

        Args:
            start: int, the start of the range.
            end: int, the end of the range (inclusive).
        """
        for num in range(start, end + 1):
            if IsPerfect.check(num):
                print(num)