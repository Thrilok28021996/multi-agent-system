"""
Subtract operation module with input validation.

Provides a robust subtract function that handles various input types
and validates them before performing the operation.
"""

from numbers import Real
from typing import Union

Number = Union[int, float]


def subtract(a: Number, b: Number) -> Number:
    """
    Subtract b from a with strict input validation.

    Parameters
    ----------
    a : int or float
        The minuend (value to subtract from).
    b : int or float
        The subtrahend (value to subtract).

    Returns
    -------
    int or float
        The result of a - b.

    Raises
    ------
    TypeError
        If either a or b is not a real number (int, float, or other Real
        numeric subclass), or is a boolean (which is a subclass of int but
        is not meaningful for arithmetic here).
    ValueError
        If either input is NaN or a positive/negative infinity when
        such a result would be non-finite in a way callers likely
        did not intend.
    """
    # Reject None explicitly with a clear message
    if a is None or b is None:
        raise TypeError(
            f"subtract() arguments must be real numbers, not None "
            f"(got a={a!r}, b={b!r})"
        )

    # Reject bool explicitly: bool is a subclass of int but rarely
    # intended in arithmetic, so we treat it as invalid.
    if isinstance(a, bool) or isinstance(b, bool):
        raise TypeError(
            f"subtract() arguments must be real numbers, not bool "
            f"(got a={type(a).__name__}, b={type(b).__name__})"
        )

    # Allow only real numeric types (int, float, Decimal, Fraction, etc.)
    if not isinstance(a, Real) or not isinstance(b, Real):
        raise TypeError(
            f"subtract() arguments must be real numbers "
            f"(int, float, or Real subclass). "
            f"Got a={type(a).__name__}, b={type(b).__name__}."
        )

    result = a - b

    # Validate the result is a usable number
    if isinstance(result, float):
        import math
        if math.isnan(result):
            raise ValueError(f"subtract() produced NaN (a={a!r}, b={b!r})")
        if math.isinf(result):
            raise ValueError(
                f"subtract() produced non-finite result "
                f"(a={a!r}, b={b!r}, result={result!r})"
            )

    return result


def _run_self_tests() -> None:
    """Lightweight inline self-tests for the subtract function."""
    test_cases = [
        # (a, b, expected)
        (10, 3, 7),
        (0, 0, 0),
        (-5, -3, -2),
        (3.5, 1.25, 2.25),
        (0, 7, -7),
    ]

    for a, b, expected in test_cases:
        got = subtract(a, b)
        assert got == expected, f"subtract({a}, {b}) = {got}, expected {expected}"

    # Validation failure cases — each must raise.
    failure_cases = [
        (None, 1, TypeError),
        (1, None, TypeError),
        ("5", 1, TypeError),
        (1, "2", TypeError),
        (True, 1, TypeError),
        (1, False, TypeError),
        ([1, 2], 1, TypeError),
        (1, {"x": 1}, TypeError),
    ]
    for a, b, exc_type in failure_cases:
        try:
            subtract(a, b)
        except exc_type:
            pass
        else:
            raise AssertionError(
                f"subtract({a!r}, {b!r}) should have raised {exc_type.__name__}"
            )

    print("All subtract() self-tests passed.")


if __name__ == "__main__":
    # Example usage
    print("subtract(10, 3) =", subtract(10, 3))
    print("subtract(3.5, 1.25) =", subtract(3.5, 1.25))
    print("subtract(-5, -3) =", subtract(-5, -3))

    # Run self-tests
    _run_self_tests()
