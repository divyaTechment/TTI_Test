"""Unit tests for impact explanation formatting."""
from datadog_tia import format_impact_explanation


def test_format_impact_explanation_plain():
    changed = ["src/foo.py", "src/bar.py"]
    mapping = {
        "src/foo.py": {
            "impacted_files": {"module.foo", "src/foo.py"},
            "tests": {"tests/test_foo.py::test_thing", "tests/test_foo.py::test_other"},
        },
        "src/bar.py": {"impacted_files": set(), "tests": set()},
    }

    text = format_impact_explanation(changed, mapping, use_color=False)

    assert "Code Change & Dependency View" in text
    assert "src/foo.py" in text
    assert "module.foo" in text
    assert "tests/test_foo.py::test_thing" in text
    assert "No dependent files found." in text
    assert "src/bar.py" in text
