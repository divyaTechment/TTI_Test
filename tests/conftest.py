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
        # Normalize changed file/method format
        # Convert app.calculator -> app/calculator for matching
        if "." in cf and "/" not in cf:
            # Format: app.calculator or app.calculator.add
            cf_normalized = cf.replace(".", "/", 1)  # Only replace first dot
            if "." in cf_normalized:
                # Has method: app/calculator.add
                cf_parts = cf_normalized.split(".", 1)
                cf_file_norm = cf_parts[0]  # app/calculator
                cf_method = cf_parts[1] if len(cf_parts) > 1 else None
            else:
                # File only: app/calculator
                cf_file_norm = cf_normalized
                cf_method = None
        else:
            # Already in app/calculator format
            if "." in cf:
                cf_parts = cf.split(".", 1)
                cf_file_norm = cf_parts[0]
                cf_method = cf_parts[1] if len(cf_parts) > 1 else None
            else:
                cf_file_norm = cf
                cf_method = None
        
        for imp in impacted_files:
            # Extract file and method from impact marker (format: app/calculator.add)
            if "." in imp:
                imp_parts = imp.split(".", 1)
                imp_file = imp_parts[0]  # app/calculator
                imp_method = imp_parts[1] if len(imp_parts) > 1 else None
            else:
                imp_file = imp
                imp_method = None
            
            # Exact match
            if imp == cf or imp_file == cf_file_norm:
                if cf_method is None or imp_method == cf_method:
                    return True
            
            # File path match (normalize both)
            imp_file_norm = imp_file.replace("\\", "/")
            cf_file_norm_clean = cf_file_norm.replace("\\", "/")
            
            if imp_file_norm == cf_file_norm_clean:
                # Same file - if no method specified in changed, match all methods
                if cf_method is None:
                    return True
                # If method specified, check method match
                if imp_method == cf_method:
                    return True
            
            # Check if file paths match (one contains the other)
            if imp_file_norm in cf_file_norm_clean or cf_file_norm_clean in imp_file_norm:
                if cf_method is None:
                    # File-level change matches all methods in that file
                    return True
                elif imp_method == cf_method:
                    # Method-level match
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

