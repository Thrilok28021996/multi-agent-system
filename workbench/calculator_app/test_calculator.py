"""Unit tests for the calculator module."""
import pytest

from calculator import add, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(0, 5) == -5
    assert subtract(-3, -2) == -1


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 100) == 0


def test_divide():
    assert divide(10, 2) == 5
    assert divide(-9, 3) == -3
    assert divide(0, 5) == 0


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        divide(5, 0)
