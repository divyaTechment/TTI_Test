"""Tests for multiplication functionality."""
import pytest
from app.calculator import multiply


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
def test_multiply_positive():
    """Test multiplication of positive numbers."""
    assert multiply(3, 4) == 12


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
def test_multiply_negative():
    """Test multiplication with negative numbers."""
    assert multiply(-3, -4) == 12
    assert multiply(-3, 4) == -12


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
def test_multiply_zero():
    """Test multiplication with zero."""
    assert multiply(5, 0) == 0
    assert multiply(0, 5) == 0

