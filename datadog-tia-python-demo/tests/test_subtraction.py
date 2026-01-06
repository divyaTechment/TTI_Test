import pytest
from app.calculator import subtract


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_positive():
    assert subtract(5, 3) == 2


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_subtract_negative():
    assert subtract(0, 5) == -5
