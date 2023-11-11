import pytest

from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.semantic_elements.table_element.table_element import TableElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "simple",
            """
                <div>
                <div>
                <table>
                    <tr>
                        <td>Row 1 content</td>
                    </tr>
                    <tr>
                        <td>Row 2 content</td>
                    </tr>
                </table>
                </div>
                </div>
            """,
            [
                {"type": TableElement, "tag": "div"},
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_table_classifier(name, html_str, expected_elements):
    """
    test_table_classifier test checks that the TableClassifier can successfully
    transform a list of semantic elements returned by `parse_initial_semantic_elements`.
    """
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = TableClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
