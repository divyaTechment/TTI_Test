"""Helpers for Datadog TIA demo impact explanation view.

Provides `format_impact_explanation` which renders a textual view that groups
changed files -> dependent (impacted) files -> tests. Colors can be toggled off
for tests.
"""
from __future__ import annotations

from typing import Dict, Iterable

# ANSI colors
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"


def _color(s: str, color: str, use_color: bool) -> str:
    return f"{color}{s}{RESET}" if use_color else s


def format_impact_explanation(changed_files: Iterable[str], mapping: Dict[str, Dict[str, set]], use_color: bool = True) -> str:
    """Return a multi-line string explaining why tests were impacted.

    mapping shape: { changed_file: { 'impacted_files': set(...), 'tests': set(...) } }
    """
    lines = []
    lines.append("Code Change & Dependency View (Why impacted?)")
    lines.append("")
    lines.append("Changed files:")

    for cf in changed_files:
        lines.append(f"  - {_color(cf, RED, use_color)}")
        impacted = sorted(mapping.get(cf, {}).get("impacted_files", []))
        tests = sorted(mapping.get(cf, {}).get("tests", []))

        if impacted:
            lines.append("    Dependent files:")
            for imp in impacted:
                lines.append(f"      - {_color(imp, YELLOW, use_color)}")
        else:
            lines.append("    No dependent files found.")

        if tests:
            lines.append("    Tests:")
            for t in tests:
                lines.append(f"      - {_color(t, BLUE, use_color)}")
        else:
            lines.append("    No tests found for these dependencies.")

        lines.append("")

    lines.append("(Legend: \u001b[31mchanged\u001b[0m / \u001b[33mdependent\u001b[0m / \u001b[34mtests\u001b[0m)")
    return "\n".join(lines)
