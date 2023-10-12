from dataclasses import asdict
from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.highlighted_text_element import (
    HighlightedTextElement,
    TextStyle,
)


def test_highlighted_text_element_initialization():
    # Arrange
    mock_html_tag = Mock()

    # Act & Assert
    with pytest.raises(
        ValueError,
        match="styles must be specified for HighlightedElement",
    ):
        HighlightedTextElement(mock_html_tag, style=None)


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    tag.string = "A" * 60
    style = TextStyle(bold_with_font_weight=True, italic=True)

    # Act
    actual = HighlightedTextElement(HtmlTag(tag), style=style).to_dict()

    # Assert
    assert actual["text_style"] == asdict(style)
