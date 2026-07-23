"""Tests for the main module."""

from myproject import __version__
from myproject.main import greet, main


class TestGreet:
    """Tests for the greet function."""

    def test_greet_default(self) -> None:
        """Test greet with default argument."""
        assert greet() == "Hello, World!"

    def test_greet_custom_name(self) -> None:
        """Test greet with a custom name."""
        assert greet("Alice") == "Hello, Alice!"

    def test_greet_empty_string(self) -> None:
        """Test greet with an empty string."""
        assert greet("") == "Hello, !"


class TestMain:
    """Tests for the main function."""

    def test_main_runs(self, capsys) -> None:
        """Test that main runs without error."""
        main()
        captured = capsys.readouterr()
        assert f"myproject v{__version__}" in captured.out
        assert "Hello, World!" in captured.out
