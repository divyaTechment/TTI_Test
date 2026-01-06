"""Parametrized tests for calculator operations."""
import pytest
from app.calculator import add, subtract, multiply, divide


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1.5, 2.5, 4.0),
    (-5, 5, 0),
    (10**6, 1, 1000001),
    (100, -50, 50),
])
def test_add_parametrized(a, b, expected):
    """Parametrized test for addition."""
    assert add(a, b) == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
@pytest.mark.parametrize("a,b,expected", [
    (5, 3, 2),
    (3.5, 1.5, 2.0),
    (-1, -1, 0),
    (10, 15, -5),
    (0, 5, -5),
])
def test_subtract_parametrized(a, b, expected):
    """Parametrized test for subtraction."""
    assert subtract(a, b) == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 6),
    (2.5, 4, 10.0),
    (-2, 3, -6),
    (0, 100, 0),
])
def test_multiply_parametrized(a, b, expected):
    """Parametrized test for multiplication."""
    assert multiply(a, b) == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5),
    (15, 3, 5),
    (7, 2, 3.5),
    (-10, 2, -5),
])
def test_divide_parametrized(a, b, expected):
    """Parametrized test for division."""
    assert divide(a, b) == pytest.approx(expected)
