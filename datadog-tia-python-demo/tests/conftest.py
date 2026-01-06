"""Pytest helpers for Datadog TIA demo.

Provides a simple `--changed-files` option and `impact` marker to filter tests
based on changed files. This simulates selecting 'impacted' tests when files
change (useful to demo Datadog test-selection behavior locally).
"""
from __future__ import annotations

from typing import List
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--changed-files",
        action="store",
        default="",
        help="Comma-separated list of changed files (simulates git changes)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "impact(files): mark test as impacted by given files or symbols",
    )


def _collect_marker_files(marker) -> List[str]:
    files = []
    for arg in marker.args:
        if isinstance(arg, (list, tuple)):
            files.extend(arg)
        else:
            files.append(str(arg))
    return files


def _matches_changed(impacted_files: List[str], changed_files: List[str]) -> bool:
    for cf in changed_files:
        for imp in impacted_files:
            # Loose matching: check substrings and suffixes
            if imp in cf or cf.endswith(imp) or cf == imp:
                return True
    return False


def pytest_collection_modifyitems(config, items):
    changed_files_opt = config.getoption("--changed-files")
    if not changed_files_opt:
        return

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
        print(f"Selected {len(impacted_items)} impacted tests based on changed files: {changed}")
