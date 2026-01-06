import pytest

from app.calculator import add, subtract


@pytest.mark.unit
@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1.5, 2.5, 4.0),
    (-5, 5, 0),
    (10**6, 1, 1000001),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.parametrize("a,b,expected", [
    (5, 3, 2),
    (3.5, 1.5, 2.0),
    (-1, -1, 0),
])
def test_subtract_parametrized(a, b, expected):
    assert subtract(a, b) == pytest.approx(expected)
