from unittest.mock import patch

import bs4
import pytest
from bs4 import NavigableString

from sec_parser.processing_engine.html_tag import EmptyNavigableStringError, HtmlTag


# Test when input is a non-empty bs4.NavigableString object
def test_init_with_non_empty_navigable_string():
    # Arrange
    nav_string = NavigableString("Hello")

    # Act
    with patch("warnings.warn") as mock_warn:
        html_tag = HtmlTag(nav_string)

    # Assert
    mock_warn.assert_called()
    tag = html_tag._bs4  # separate variable for readability
    assert isinstance(tag, bs4.Tag)
    assert tag.name == "span"
    assert tag.string == "Hello"


# Test when input is an empty bs4.NavigableString object
def test_init_with_empty_navigable_string():
    # Arrange
    nav_string = NavigableString("")

    # Act & Assert
    with pytest.raises(EmptyNavigableStringError):
        HtmlTag(nav_string)


# Test when input is neither bs4.Tag nor bs4.NavigableString
def test_init_with_unsupported_type():
    # Arrange
    unsupported_element = 42  # an integer

    # Act & Assert
    with pytest.raises(TypeError):
        HtmlTag(unsupported_element)
