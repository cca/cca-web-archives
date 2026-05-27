import pytest

from ia.wb_coverage import sanitize_filename


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
