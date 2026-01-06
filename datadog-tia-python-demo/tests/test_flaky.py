import os
import random
import pytest

from app.calculator import add


@pytest.mark.unit
@pytest.mark.impact("app/calculator.add")
def test_flaky_random():
    """Flaky test: 50% chance to pass.

    To reproduce deterministically, set FLAKY_SEED environment variable.
    """
    seed = int(os.environ.get("FLAKY_SEED", "0"))
    if seed:
        random.seed(seed)
    assert random.choice([True, False])
