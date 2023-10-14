import pytest

from sec_parser.processing_steps.table_classifier import TableClassifier
from sec_parser.semantic_elements.table_element import TableElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
    [
        (
            """
                <div>
                <div>
                <table></table>
                </div>
                </div>
            """,
            [
                {"type": TableElement, "tag": "div"},
            ],
        ),
    ],
)
def test_table_classifier(html_str, expected_elements):
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
