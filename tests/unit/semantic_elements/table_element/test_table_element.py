from dataclasses import asdict
from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.table_element.table_element import TableElement
from sec_parser.utils.bs4_.approx_table_metrics import ApproxTableMetrics


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "rows": 0,
            "numbers": 0,
            "text": "",
            "expected_summary": "Table with ~0 rows, ~0 numbers, and 0 characters.",
        },
        {
            "rows": 5,
            "numbers": 6,
            "text": "12345",
            "expected_summary": "Table with ~5 rows, ~6 numbers, and 5 characters.",
        },
        {
            "rows": 10,
            "numbers": 11,
            "text": "1234567890",
            "expected_summary": "Table with ~10 rows, ~11 numbers, and 10 characters.",
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
    table_element = TableElement(mock_semantic_element)

    # Act
    result = table_element.get_summary()

    # Assert
    assert result == expected_summary


def test_to_dict():
    # Arrange
    mock_semantic_element = Mock(spec=HtmlTag)
    mock_semantic_element.get_approx_table_metrics.return_value = ApproxTableMetrics(
        5, 6
    )
    mock_semantic_element.to_dict.return_value = (
        {}
    )  # Mock the to_dict method to return an empty dictionary

    table_element = TableElement(mock_semantic_element)

    # Act
    actual = table_element.to_dict()

    # Assert
    assert actual["metrics"] == asdict(ApproxTableMetrics(5, 6))


def test_table_to_markdown():
    # Arrange
    from bs4 import BeautifulSoup

    table_html = """
    <table>
        <tr>
            <th>Header 1</th>
        </tr>
        <tr>
            <td>Cell 1</td>
        </tr>
    </table>
    """
    table = BeautifulSoup(table_html, "lxml").table
    assert isinstance(table, bs4.Tag)
    table_element = TableElement(HtmlTag(table))

    # Act
    markdown_result = table_element.table_to_markdown()

    # Assert
    assert isinstance(markdown_result, str)
    assert markdown_result == "| Header 1 |\n|---|\n| Cell 1 |"
