"""Unit tests for the calculator module."""
import pytest

import calculator


class TestAdd:
    def test_positive_numbers(self):
        assert calculator.add(2, 3) == 5

    def test_negative_numbers(self):
        assert calculator.add(-2, -3) == -5

    def test_mixed_signs(self):
        assert calculator.add(-1, 1) == 0

    def test_floats(self):
        assert calculator.add(0.1, 0.2) == pytest.approx(0.3)


class TestSubtract:
    def test_positive_result(self):
        assert calculator.subtract(5, 3) == 2

    def test_negative_result(self):
        assert calculator.subtract(3, 5) == -2

    def test_zero(self):
        assert calculator.subtract(0, 0) == 0


class TestMultiply:
    def test_positive_numbers(self):
        assert calculator.multiply(4, 3) == 12

    def test_by_zero(self):
        assert calculator.multiply(0, 100) == 0

    def test_negatives(self):
        assert calculator.multiply(-2, -3) == 6


class TestDivide:
    def test_exact(self):
        assert calculator.divide(10, 2) == 5

    def test_non_exact(self):
        assert calculator.divide(7, 2) == 3.5

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError):
            calculator.divide(1, 0)


class TestPower:
    def test_positive_exponent(self):
        assert calculator.power(2, 3) == 8

    def test_zero_exponent(self):
        assert calculator.power(5, 0) == 1

    def test_negative_exponent(self):
        assert calculator.power(2, -1) == 0.5
