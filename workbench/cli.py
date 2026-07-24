"""Command-line interface for the calculator.

Provides an interactive REPL for performing arithmetic operations.
"""
import calculator


OPERATIONS = {
    '+': calculator.add,
    '-': calculator.subtract,
    '*': calculator.multiply,
    '/': calculator.divide,
    '^': calculator.power,
}


def parse_input(user_input):
    """Parse a user input string into (a, op, b).

    Args:
        user_input: A string like "3 + 4".

    Returns:
        A tuple of (a, op, b) where a and b are floats and op is a string.

    Raises:
        ValueError: If the input is malformed or the operator is unknown.
    """
    parts = user_input.strip().split()
    if len(parts) != 3:
        raise ValueError("Input must be in the form: <number> <op> <number>")

    a_str, op, b_str = parts
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        raise ValueError("Both operands must be numbers")

    if op not in OPERATIONS:
        raise ValueError(f"Unknown operator '{op}'. Valid: {', '.join(OPERATIONS)}")

    return a, op, b


def evaluate(a, op, b):
    """Evaluate a single operation."""
    return OPERATIONS[op](a, b)


def main():
    """Run the interactive calculator REPL."""
    print("Calculator REPL (type 'quit' to exit)")
    print("Usage: <number> <op> <number>   e.g.  3 + 4")
    while True:
        try:
            user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.strip().lower() in ('quit', 'exit'):
            print("Goodbye.")
            break

        try:
            a, op, b = parse_input(user_input)
            result = evaluate(a, op, b)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        print(result)


if __name__ == "__main__":
    main()
