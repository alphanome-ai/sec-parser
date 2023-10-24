import pytest

from sec_parser.utils.py_utils import clean_whitespace, normalize_string


# Test for normal cases
@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("Hello World", "hello world"),  # Simple case
        ("HELLO WORLD", "hello world"),  # All uppercase
        ("hello world!", "hello world"),  # With special character
        ("  Hello  World  ", "hello world"),  # Extra spaces
        ("", ""),  # Empty string
    ],
)
def test_normalize_string_normal_cases(input_str, expected):
    # Arrange
    pass

    # Act
    result = normalize_string(input_str)

    # Assert
    assert result == expected


# Test for edge cases
@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("123", "123"),  # Only numbers
        ("!@#$%", ""),  # Only special characters
        (" \t \n ", ""),  # Only whitespace, tabs, and newlines
    ],
)
def test_normalize_string_edge_cases(input_str, expected):
    # Arrange
    pass

    # Act
    result = normalize_string(input_str)

    # Assert
    assert result == expected
