import pytest
from app.calculator import add


@pytest.mark.unit
def test_add_positive():
    assert add(1, 2) == 3


@pytest.mark.unit
def test_add_negative():
    assert add(-1, -1) == -2
