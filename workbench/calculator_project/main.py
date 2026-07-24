"""
main.py

Entry point for the calculator application.
Demonstrates usage of the calculator module via a simple CLI loop.
"""

from calculator import add, subtract, multiply, divide


def main():
    print("Welcome to the Calculator!")
    print("Supported operations: add, subtract, multiply, divide")
    print("Type 'quit' to exit.\n")

    while True:
        op = input("Enter operation (add/subtract/multiply/divide): ").strip().lower()
        if op == "quit":
            print("Goodbye!")
            break
        if op not in {"add", "subtract", "multiply", "divide"}:
            print("Unknown operation. Please try again.\n")
            continue

        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
        except ValueError:
            print("Invalid number. Please try again.\n")
            continue

        try:
            if op == "add":
                result = add(a, b)
            elif op == "subtract":
                result = subtract(a, b)
            elif op == "multiply":
                result = multiply(a, b)
            elif op == "divide":
                result = divide(a, b)
            print(f"Result: {result}\n")
        except ValueError as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
