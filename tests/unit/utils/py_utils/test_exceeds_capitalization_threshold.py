import pytest
from hypothesis import given
from hypothesis import strategies as st

from sec_parser.utils.py_utils import MAX_THRESHOLD, exceeds_capitalization_threshold

from sec_parser.exceptions import SecParserValueError


@pytest.mark.parametrize(
    "input_str,threshold,expected",
    [
        ("HelloWorld", 50, False),
        ("HELLOWORLD", 50, True),
        ("HELLOworld", 50, True),
        ("", 50, False),
        ("Hello123", 50, False),
        ("HELLO123", 50, True),
        ("123456", 50, False),
        ("ABCabc0000000000", 50, True),
        ("ABcabc0000000000", 50, False),
    ],
)
def test_exceeds_capitalization_threshold(input_str, threshold, expected):
    # Arrange

    # Act
    result = exceeds_capitalization_threshold(input_str, threshold)

    # Assert
    assert result == expected


# Test cases for exceptions
@pytest.mark.parametrize(
    "input_str,threshold",
    [
        ("HelloWorld", -1),
        ("HelloWorld", MAX_THRESHOLD + 1),
        ("", 101),
        ("HELLO123", -50),
        ("123456", 200),
    ],
)
def test_exceeds_capitalization_threshold_exceptions(input_str, threshold):
    with pytest.raises(SecParserValueError) as excinfo:
        exceeds_capitalization_threshold(input_str, threshold)
    assert str(excinfo.value) == "Threshold must be between 0 and 100."
