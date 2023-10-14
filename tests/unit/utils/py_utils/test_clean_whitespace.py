import re

import pytest

# Hypothesis test
from hypothesis import given
from hypothesis import strategies as st

from sec_parser.utils.py_utils import clean_whitespace


# Test table using pytest.mark.parametrize
@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        (
            "  Hello \n world  ",
            "Hello world",
        ),  # Test with leading/trailing spaces and a newline
        (
            "\n\nMultiple\n newlines and \t\ttabs.",
            "Multiple newlines and tabs.",
        ),  # Test with multiple newlines and tabs
        ("NoSpacesOrNewLines", "NoSpacesOrNewLines"),  # Test with no spaces or newlines
        ("", ""),  # Test with an empty string
        ("     ", ""),  # Test with only spaces
        ("  \n\t  ", ""),  # Test with mixed whitespace characters
    ],
)
def test_clean_whitespace(input_str, expected_output):
    # Act
    cleaned_str = clean_whitespace(input_str)

    # Assert
    assert cleaned_str == expected_output


# Hypothesis test
@given(st.text(min_size=0, max_size=1000))
def test_clean_whitespace_abstract(input_str):
    # Act
    cleaned_str = clean_whitespace(input_str)

    # Assert
    assert "  " not in cleaned_str
    assert cleaned_str == cleaned_str.strip()
    assert "\n" not in cleaned_str
    assert len(cleaned_str) <= len(input_str)
