import pytest

from app.calculator import add, subtract


@pytest.mark.full
def test_sequence_operations():
    """Full test: perform a sequence of operations and validate final result."""
    result = 0
    result = add(result, 10)
    result = subtract(result, 3)
    result = add(result, 2.5)
    result = subtract(result, 1)

    # Expected: 0 + 10 - 3 + 2.5 - 1 = 8.5
    assert result == pytest.approx(8.5)


@pytest.mark.full
def test_large_numbers_and_precision():
    """Full test: exercise large integers and float precision behavior."""
    large = 10 ** 12
    a = add(large, large)
    assert a == 2 * large

    b = subtract(1.0000001, 0.0000001)
    assert b == pytest.approx(1.0, rel=1e-9)
