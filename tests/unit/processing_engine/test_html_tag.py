from unittest.mock import patch

import bs4
import pytest
from bs4 import NavigableString

from sec_parser.processing_engine.html_tag import EmptyNavigableStringError, HtmlTag


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


def test_init_with_empty_navigable_string():
    # Arrange
    nav_string = NavigableString("")

    # Act & Assert
    with pytest.raises(EmptyNavigableStringError):
        HtmlTag(nav_string)


def test_init_with_unsupported_type():
    # Arrange
    unsupported_element = 42  # an integer

    # Act & Assert
    with pytest.raises(TypeError):
        HtmlTag(unsupported_element)


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    tag.string = "A" * 60

    # Act
    actual = HtmlTag(tag).to_dict()

    # Assert
    assert actual == {
        "tag_name": "span",
        "text_preview": "AAAAAAAAAAAAAAAAAAAA...[20]...AAAAAAAAAAAAAAAAAAAA",
        "html_preview": "<span>AAAAAAAAAAAAAA...[33]...AAAAAAAAAAAAA</span>",
        "html_hash": "3836a62b",
    }
