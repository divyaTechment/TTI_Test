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
        help="Comma-separated list of changed files or methods (e.g., 'app/calculator.py,app/calculator.add')",
    )
    parser.addoption(
        "--changed-methods",
        action="store",
        default="",
        help="Comma-separated list of changed methods (e.g., 'app/calculator.add,app/calculator.subtract')",
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
    """Check if any impacted file or method matches changed files/methods."""
    for cf in changed_files:
        for imp in impacted_files:
            # Method-level matching: e.g., "app/calculator.add" matches "app/calculator.add" or "app/calculator.py" with add method
            if imp == cf:
                return True
            # File-level matching: check if changed file path matches impact marker
            if imp in cf or cf.endswith(imp):
                return True
            # Method-level matching: if impact is "app/calculator.add" and changed is "app/calculator.add" or contains ".add"
            if "." in imp and "." in cf:
                # Extract method name from impact (e.g., "app/calculator.add" -> "add")
                imp_parts = imp.split(".")
                cf_parts = cf.split(".")
                if len(imp_parts) > 1 and len(cf_parts) > 1:
                    imp_method = imp_parts[-1]
                    cf_method = cf_parts[-1]
                    # Check if file path matches and method name matches
                    imp_file = ".".join(imp_parts[:-1])
                    cf_file = ".".join(cf_parts[:-1])
                    if imp_file in cf_file or cf_file.endswith(imp_file.replace("/", ".")):
                        if imp_method == cf_method:
                            return True
    return False


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on changed files/methods and custom options."""
    # Combine changed files and changed methods
    changed_files_opt = config.getoption("--changed-files")
    changed_methods_opt = config.getoption("--changed-methods")
    
    changed = []
    if changed_files_opt:
        changed.extend([p.strip() for p in changed_files_opt.split(",") if p.strip()])
    if changed_methods_opt:
        changed.extend([p.strip() for p in changed_methods_opt.split(",") if p.strip()])
    
    if changed:
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
            print(f"\n[Test Optimization] Selected {len(impacted_items)} impacted tests based on changed files/methods: {changed}")
            print(f"[Test Optimization] Deselected {len(deselected)} non-impacted tests")

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

