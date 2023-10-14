from unittest.mock import Mock

import pytest

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

# Test data table
test_data = [
    {"pretty": False, "expected_result": "<html>sample</html>"},
    {"pretty": True, "expected_result": "<html>\n  sample\n</html>"},
]


@pytest.mark.parametrize("test_case", test_data)
def test_get_source_code(test_case):
    # Arrange
    pretty = test_case["pretty"]
    expected_result = test_case["expected_result"]
    mock_html_tag = Mock()
    mock_html_tag.get_source_code.return_value = expected_result
    semantic_element = AbstractSemanticElement(html_tag=mock_html_tag)

    # Act
    result = semantic_element.get_source_code(pretty=pretty)

    # Assert
    assert result == expected_result
    mock_html_tag.get_source_code.assert_called_once_with(pretty=pretty)
