"""Flaky tests to demonstrate Datadog TIA flaky test detection.

These tests are designed to fail intermittently to showcase
Datadog's flaky test detection and reporting capabilities.
"""
import os
import random
import time
import pytest
from app.calculator import add, subtract


@pytest.mark.unit
@pytest.mark.flaky
@pytest.mark.impact("app/calculator.add")
def test_flaky_random():
    """Flaky test: 50% chance to pass based on random choice.
    
    To reproduce deterministically, set FLAKY_SEED environment variable.
    """
    seed = int(os.environ.get("FLAKY_SEED", "0"))
    if seed:
        random.seed(seed)
    assert random.choice([True, False])


@pytest.mark.unit
@pytest.mark.flaky
@pytest.mark.impact("app/calculator.add")
def test_flaky_time_based():
    """Flaky test: fails during odd seconds (time-based flakiness)."""
    current_second = int(time.time()) % 60
    # Fail if current second is odd
    assert current_second % 2 == 0, f"Failed at second {current_second}"


@pytest.mark.unit
@pytest.mark.flaky
@pytest.mark.impact("app/calculator.subtract")
def test_flaky_conditional():
    """Flaky test: fails based on environment variable."""
    flaky_mode = os.environ.get("FLAKY_MODE", "pass")
    if flaky_mode == "fail":
        pytest.fail("Flaky test failed due to FLAKY_MODE=fail")


@pytest.mark.unit
@pytest.mark.flaky
@pytest.mark.impact("app/calculator.add")
def test_flaky_race_condition():
    """Flaky test: simulates race condition with timing."""
    import threading
    
    result = [0]
    
    def increment():
        time.sleep(0.001 * random.random())
        result[0] += 1
    
    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Sometimes fails due to race condition simulation
    assert result[0] == 10 or random.random() < 0.3


@pytest.mark.unit
@pytest.mark.flaky
@pytest.mark.impact("app/calculator.add")
def test_flaky_floating_point():
    """Flaky test: floating point precision issues."""
    # This might fail due to floating point precision
    result = add(0.1, 0.2)
    # Sometimes the assertion might fail due to precision
    assert result == pytest.approx(0.3) or random.random() < 0.4

