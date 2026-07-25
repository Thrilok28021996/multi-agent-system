"""Unit tests for the calculator module."""

import unittest

from calculator import add, divide, modulo, multiply, power, subtract


class TestCalculator(unittest.TestCase):
    """Test cases for calculator operations."""

    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(10, 15), 25)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)
        self.assertEqual(add(-5, 5), 0)

    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(7, 0), 7)

    def test_add_floats(self):
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)

    def test_subtract_positive_numbers(self):
        self.assertEqual(subtract(10, 4), 6)
        self.assertEqual(subtract(0, 5), -5)

    def test_subtract_negative_result(self):
        self.assertEqual(subtract(3, 10), -7)

    def test_subtract_zero(self):
        self.assertEqual(subtract(5, 0), 5)
        self.assertEqual(subtract(0, 0), 0)

    def test_multiply_positive_numbers(self):
        self.assertEqual(multiply(6, 7), 42)
        self.assertEqual(multiply(1, 100), 100)

    def test_multiply_by_zero(self):
        self.assertEqual(multiply(0, 100), 0)
        self.assertEqual(multiply(100, 0), 0)

    def test_multiply_negative_numbers(self):
        self.assertEqual(multiply(-3, 4), -12)
        self.assertEqual(multiply(-3, -4), 12)

    def test_divide_positive_numbers(self):
        self.assertEqual(divide(20, 5), 4)
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

    def test_divide_result_is_float(self):
        self.assertEqual(divide(10, 4), 2.5)

    def test_power(self):
        self.assertEqual(power(2, 8), 256)
        self.assertEqual(power(5, 0), 1)
        self.assertEqual(power(10, 1), 10)

    def test_modulo(self):
        self.assertEqual(modulo(17, 5), 2)
        self.assertEqual(modulo(10, 3), 1)

    def test_modulo_by_zero_raises(self):
        with self.assertRaises(ValueError):
            modulo(10, 0)


if __name__ == "__main__":
    unittest.main()
