"""Tests for subtraction functionality."""
import pytest
from app.calculator import subtract


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_positive():
    """Test subtraction of positive numbers."""
    assert subtract(5, 3) == 2


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_negative():
    """Test subtraction resulting in negative numbers."""
    assert subtract(0, 5) == -5


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_mixed():
    """Test subtraction with mixed positive and negative numbers."""
    assert subtract(5, -3) == 8
    assert subtract(-5, 3) == -8


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_zero():
    """Test subtraction with zero."""
    assert subtract(5, 0) == 5
    assert subtract(0, 0) == 0
