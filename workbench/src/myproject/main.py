"""Main entry point for myproject."""

from myproject import __version__


def greet(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


def main() -> None:
    """Main entry point of the application."""
    message = greet()
    print(f"myproject v{__version__}")
    print(message)


if __name__ == "__main__":
    main()
