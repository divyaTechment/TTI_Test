"""Integration tests for calculator operations."""
import pytest
from app.calculator import add, subtract, multiply, divide


@pytest.mark.integration
@pytest.mark.impact("app/calculator")
def test_sequence_operations():
    """Integration test: perform a sequence of operations and validate final result."""
    result = 0
    result = add(result, 10)
    result = subtract(result, 3)
    result = multiply(result, 2)
    result = divide(result, 2)
    result = add(result, 2.5)
    result = subtract(result, 1)

    # Expected: ((0 + 10 - 3) * 2 / 2) + 2.5 - 1 = 8.5
    assert result == pytest.approx(8.5)


@pytest.mark.integration
@pytest.mark.impact("app/calculator")
def test_large_numbers_and_precision():
    """Integration test: exercise large integers and float precision behavior."""
    large = 10 ** 12
    a = add(large, large)
    assert a == 2 * large

    b = subtract(1.0000001, 0.0000001)
    assert b == pytest.approx(1.0, rel=1e-9)


@pytest.mark.integration
@pytest.mark.impact("app/calculator")
def test_complex_calculation():
    """Integration test: complex calculation involving all operations."""
    # Calculate: (10 + 5) * 2 - 20 / 4
    step1 = add(10, 5)  # 15
    step2 = multiply(step1, 2)  # 30
    step3 = divide(20, 4)  # 5
    result = subtract(step2, step3)  # 25
    
    assert result == 25


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.impact("app/calculator")
def test_performance_large_dataset():
    """Integration test: performance test with large dataset."""
    numbers = list(range(1000))
    result = 0
    
    for num in numbers:
        result = add(result, num)
    
    # Sum of 0 to 999 = 499500
    assert result == 499500

