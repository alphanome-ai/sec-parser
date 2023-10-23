from unittest.mock import Mock, patch

import pytest

from sec_parser.semantic_elements.table_element import TableElement
from sec_parser.utils.bs4_.approx_table_metrics import ApproxTableMetrics


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "rows": 0,
            "numbers": 0,
            "text": "",
            "expected_summary": "Table with 0 rows, 0 numbers, and 0 characters.",
        },
        {
            "rows": 5,
            "numbers": 6,
            "text": "12345",
            "expected_summary": "Table with 5 rows, 6 numbers, and 5 characters.",
        },
        {
            "rows": 10,
            "numbers": 11,
            "text": "1234567890",
            "expected_summary": "Table with 10 rows, 11 numbers, and 10 characters.",
        },
    ],
)
def test_table_element_get_summary(test_case):
    # Arrange
    rows = test_case["rows"]
    numbers = test_case["numbers"]
    text = test_case["text"]
    expected_summary = test_case["expected_summary"]
    mock_semantic_element = Mock()
    mock_semantic_element.text = text
    mock_semantic_element.get_approx_table_metrics.return_value = ApproxTableMetrics(
        rows,
        numbers,
    )
    table_element = TableElement(html_tag=mock_semantic_element)

    # Act
    result = table_element.get_summary()

    # Assert
    assert result == expected_summary
