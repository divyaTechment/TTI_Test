import pytest


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_skipped_demo():
    """A skipped test to demonstrate reporting of skipped tests."""
    pytest.skip("Skipping this test to demonstrate skipped tests in Datadog TIA")
