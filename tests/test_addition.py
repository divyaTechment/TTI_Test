"""Tests for addition functionality."""
import pytest
from app.calculator import add


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_add_positive():
    """Test addition of positive numbers."""
    assert add(1, 2) == 3


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_add_negative():
    """Test addition of negative numbers."""
    assert add(-1, -1) == -2


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_add_mixed():
    """Test addition of positive and negative numbers."""
    assert add(5, -3) == 2
    assert add(-5, 3) == -2


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_add_zero():
    """Test addition with zero."""
    assert add(0, 0) == 0
    assert add(5, 0) == 5
    assert add(0, 5) == 5
