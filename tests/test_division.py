"""Tests for division functionality."""
import pytest
from app.calculator import divide


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
def test_divide_positive():
    """Test division of positive numbers."""
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
def test_divide_negative():
    """Test division with negative numbers."""
    assert divide(-10, 2) == -5
    assert divide(10, -2) == -5
    assert divide(-10, -2) == 5


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
def test_divide_float_result():
    """Test division resulting in float."""
    assert divide(7, 2) == 3.5
    assert divide(1, 3) == pytest.approx(0.3333333333)


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
def test_divide_by_zero():
    """Test division by zero raises error."""
    with pytest.raises(ValueError, match="Division by zero"):
        divide(5, 0)

