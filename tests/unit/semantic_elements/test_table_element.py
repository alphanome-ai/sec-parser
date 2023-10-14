from unittest.mock import Mock

import pytest

from sec_parser.semantic_elements.table_element import TableElement

# Test data table
test_data = [
    {"text": "", "expected_summary": "0 characters."},
    {"text": "12345", "expected_summary": "5 characters."},
    {"text": "1234567890", "expected_summary": "10 characters."},
]


@pytest.mark.parametrize("test_case", test_data)
def test_table_element_get_summary(test_case):
    # Arrange
    text = test_case["text"]
    expected_summary = test_case["expected_summary"]
    mock_semantic_element = Mock()
    mock_semantic_element.text = text
    table_element = TableElement(html_tag=mock_semantic_element)

    # Act
    result = table_element.get_summary()

    # Assert
    assert result == expected_summary
