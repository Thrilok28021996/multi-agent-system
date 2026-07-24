"""
Multiply operation module with input validation.
"""


def multiply(a, b):
    """
    Multiply two numbers with comprehensive input validation.

    Args:
        a: The first number to multiply.
        b: The second number to multiply.

    Returns:
        The product of a and b.

    Raises:
        TypeError: If either a or b is not a number (int, float, or bool).
        ValueError: If either a or b is NaN (Not a Number).
    """
    # Validate first operand
    _validate_numeric(a, "a")

    # Validate second operand
    _validate_numeric(b, "b")

    # Reject NaN values explicitly
    if isinstance(a, float) and a != a:
        raise ValueError("Argument 'a' must not be NaN.")
    if isinstance(b, float) and b != b:
        raise ValueError("Argument 'b' must not be NaN.")

    return a * b


def _validate_numeric(value, name):
    """
    Validate that the given value is a numeric type.

    Args:
        value: The value to validate.
        name: The name of the argument (used for error messages).

    Raises:
        TypeError: If value is not a number.
    """
    # bool is a subclass of int, so explicitly reject it for stricter validation
    if isinstance(value, bool):
        raise TypeError(
            f"Argument '{name}' must be a number (int or float), not bool."
        )

    if not isinstance(value, (int, float)):
        raise TypeError(
            f"Argument '{name}' must be a number (int or float), "
            f"got {type(value).__name__}."
        )


if __name__ == "__main__":
    # Quick demonstration / smoke tests
    print("multiply(3, 4)        =", multiply(3, 4))
    print("multiply(2.5, 4)      =", multiply(2.5, 4))
    print("multiply(-3, 7)       =", multiply(-3, 7))
    print("multiply(0, 99)       =", multiply(0, 99))

    # Validation tests
    test_cases = [
        ("3", "4"),         # strings
        (None, 5),          # None
        ([1, 2], 3),        # list
        (True, 5),          # bool
        (float('nan'), 2),  # NaN
    ]

    for a, b in test_cases:
        try:
            result = multiply(a, b)
            print(f"multiply({a!r}, {b!r}) = {result}")
        except (TypeError, ValueError) as e:
            print(f"multiply({a!r}, {b!r}) -> {type(e).__name__}: {e}")
