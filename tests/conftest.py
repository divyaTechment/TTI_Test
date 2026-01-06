"""Pytest configuration and helpers for Datadog TIA demo.

This module provides:
- Test impact markers for test selection optimization
- Changed files filtering to simulate CI/CD test selection
- Custom markers for test categorization
"""
from __future__ import annotations

from typing import List
import pytest


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--changed-files",
        action="store",
        default="",
        help="Comma-separated list of changed files (simulates git changes for test selection)",
    )
    parser.addoption(
        "--run-flaky",
        action="store_true",
        default=False,
        help="Run flaky tests (normally skipped)",
    )
    parser.addoption(
        "--run-skipped",
        action="store_true",
        default=False,
        help="Run skipped tests (normally skipped)",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "impact(files): mark test as impacted by given files or symbols",
    )
    config.addinivalue_line(
        "markers",
        "unit: quick unit tests",
    )
    config.addinivalue_line(
        "markers",
        "integration: integration tests",
    )
    config.addinivalue_line(
        "markers",
        "flaky: tests that may fail intermittently",
    )
    config.addinivalue_line(
        "markers",
        "slow: tests that take longer to run",
    )


def _collect_marker_files(marker) -> List[str]:
    """Extract file paths from impact marker."""
    files = []
    for arg in marker.args:
        if isinstance(arg, (list, tuple)):
            files.extend(arg)
        else:
            files.append(str(arg))
    return files


def _matches_changed(impacted_files: List[str], changed_files: List[str]) -> bool:
    """Check if any impacted file matches changed files."""
    for cf in changed_files:
        for imp in impacted_files:
            # Loose matching: check substrings and suffixes
            if imp in cf or cf.endswith(imp) or cf == imp:
                return True
    return False


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on changed files and custom options."""
    # Handle changed files filtering for test optimization
    changed_files_opt = config.getoption("--changed-files")
    if changed_files_opt:
        changed = [p.strip() for p in changed_files_opt.split(",") if p.strip()]
        impacted_items = []
        deselected = []

        for item in list(items):
            marker = item.get_closest_marker("impact")
            if marker:
                impacted_files = _collect_marker_files(marker)
                if _matches_changed(impacted_files, changed):
                    impacted_items.append(item)
                else:
                    deselected.append(item)
            else:
                # If a test has no impact marker, treat it as non-impacted
                deselected.append(item)

        if deselected:
            for d in deselected:
                items.remove(d)
            config.hook.pytest_deselected(items=deselected)
            print(f"\n[Test Optimization] Selected {len(impacted_items)} impacted tests based on changed files: {changed}")

    # Handle flaky test filtering
    if not config.getoption("--run-flaky"):
        skip_flaky = pytest.mark.skip(reason="Flaky tests skipped by default. Use --run-flaky to run.")
        for item in items:
            if item.get_closest_marker("flaky"):
                item.add_marker(skip_flaky)

    # Handle skipped test filtering
    # Note: This is a demo feature. In practice, tests in test_skipped.py
    # use pytest.skip() or @pytest.mark.skip() directly, so they're already skipped.
    # This option allows running them if needed for demonstration purposes.

