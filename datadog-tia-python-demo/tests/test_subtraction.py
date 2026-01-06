from app.calculator import subtract


def test_subtract_positive():
    assert subtract(5, 3) == 2


def test_subtract_negative():
    assert subtract(0, 5) == -5
