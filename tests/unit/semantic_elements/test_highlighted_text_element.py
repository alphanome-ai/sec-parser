from unittest.mock import Mock

import pytest

from sec_parser.semantic_elements.highlighted_text_element import HighlightedTextElement


def test_highlighted_text_element_initialization():
    # Arrange
    mock_html_tag = Mock()

    # Act & Assert
    with pytest.raises(
        ValueError,
        match="styles must be specified for HighlightedElement",
    ):
        HighlightedTextElement(mock_html_tag, style=None)
