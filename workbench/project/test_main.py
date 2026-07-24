"""
Test file for main.py
"""

import unittest
from main import main


class TestMain(unittest.TestCase):
    """Test cases for the main module."""

    def test_main_runs(self):
        """Test that the main function runs without error."""
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
