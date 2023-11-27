import pytest

from sec_parser.processing_steps.table_of_contents_classifier import TableOfContentsClassifier
from sec_parser.semantic_elements.table_element.table_of_contents_element import TableOfContentsElement
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
                        <td>Page</td>
                    </tr>
                </table>
                </div>
                </div>
            """,
            [
                {"type": TableOfContentsElement, "tag": "div"},
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_table_of_contents_classifier(name, html_str, expected_elements):
    """
    test_table_of_contents_classifier test checks that the TableOfContentsClassifier can successfully
    transform a list of semantic elements returned by `parse_initial_semantic_elements`.
    """
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = TableOfContentsClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)