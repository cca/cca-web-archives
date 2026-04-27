import sys
from pathlib import Path

import pytest

# Add parent directory to path to allow importing models
sys.path.insert(0, str(Path(__file__).parent.parent))

from wb_coverage import sanitize_filename


@pytest.mark.parametrize(
    "input, expected",
    [
        ("Example Site", "example-site"),
        ("  Leading and trailing spaces  ", "leading-and-trailing-spaces"),
        ("onechar?", "onechar-"),
        ("Special!@#$%^&*()Characters", "special-characters"),
        ("Mixed-CASE_and.dots", "mixed-case_and-dots"),
        ("A" * 300, "a" * 250),  # Test truncation to 250 chars
    ],
)
def test_sanitize_filename(input, expected):
    assert sanitize_filename(input) == expected
