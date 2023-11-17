from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class DummyElement(AbstractSemanticElement):
    pass


# Test data table
test_data = [
    {"pretty": False, "expected_result": "<html>sample</html>"},
    {"pretty": True, "expected_result": "<html>\n  sample\n</html>"},
]


@pytest.mark.parametrize("test_case", test_data)
def test_get_source_code(test_case):
    # Arrange
    pretty = test_case["pretty"]
    enable_compatibility = pretty
    expected_result = test_case["expected_result"]
    mock_html_tag = Mock()
    mock_html_tag.get_source_code.return_value = expected_result
    semantic_element = AbstractSemanticElement(mock_html_tag)

    # Act
    result = semantic_element.get_source_code(
        pretty=pretty,
        enable_compatibility=enable_compatibility,
    )

    # Assert
    assert result == expected_result
    mock_html_tag.get_source_code.assert_called_once_with(
        pretty=pretty,
        enable_compatibility=enable_compatibility,
    )


def test_repr():
    # Arrange
    tag = bs4.Tag(name="div")
    element = DummyElement(HtmlTag(tag))

    # Act
    repr_string = repr(element)

    # Assert
    assert repr_string == "DummyElement<div>"
