import pytest

from sec_parser.processing_steps import TopSectionManagerFor10Q
from sec_parser.semantic_elements.top_section_title import TopSectionTitle
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "simple_part_one_item_one",
            """
                <p>Part I</p>
                <p>Item 1</p>
            """,
            [
                {"type": TopSectionTitle, "tag": "p", "fields": {"level": 0}},
                {"type": TopSectionTitle, "tag": "p", "fields": {"level": 1}},
            ],
        ),
        # Add more test cases for different scenarios
    ],
    ids=[v[0] for v in values],
)
def test_top_section_manager_for_10q(name: str, html_str: str,
                                     expected_elements) -> None:
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = TopSectionManagerFor10Q()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
