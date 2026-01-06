"""Skipped tests to demonstrate Datadog TIA skipped test reporting.

These tests showcase different skip scenarios and reasons
for Datadog's test reporting and analytics.
"""
import os
import sys
import pytest
from app.calculator import add, subtract, multiply, divide


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_skipped_demo():
    """A skipped test to demonstrate reporting of skipped tests."""
    pytest.skip("Skipping this test to demonstrate skipped tests in Datadog TIA")


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
def test_skipped_condition_platform():
    """Test skipped on specific platform."""
    if sys.platform == "win32":
        pytest.skip("This test is skipped on Windows platform")


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
def test_skipped_condition_version():
    """Test skipped based on Python version."""
    if sys.version_info < (3, 8):
        pytest.skip("Requires Python 3.8 or higher")


@pytest.mark.unit
@pytest.mark.impact("app/calculator.divide")
def test_skipped_condition_env():
    """Test skipped based on environment variable."""
    if os.environ.get("SKIP_DIVISION_TESTS") == "true":
        pytest.skip("Division tests skipped via environment variable")


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
@pytest.mark.skip(reason="Feature not yet implemented")
def test_skipped_not_implemented():
    """Test for feature that is not yet implemented."""
    assert add(1, 2) == 3


@pytest.mark.unit
@pytest.mark.impact("app/calculator.subtract")
@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on macOS")
def test_skipped_skipif_macos():
    """Test skipped on macOS using skipif decorator."""
    assert subtract(10, 5) == 5


@pytest.mark.unit
@pytest.mark.impact("app/calculator.multiply")
@pytest.mark.skipif(not os.path.exists("/tmp"), reason="Requires /tmp directory")
def test_skipped_skipif_file_system():
    """Test skipped if file system requirement not met."""
    assert multiply(2, 3) == 6

