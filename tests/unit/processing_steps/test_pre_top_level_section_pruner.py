import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.pre_top_level_section_pruner import (
    PreTopLevelSectionPruner,
)
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
    TopLevelSectionTitle,
)
from tests.unit._utils import assert_elements


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


@pytest.mark.parametrize(
    ("elements", "expected_elements"),
    [
        (
            [],
            [],
        ),
        (
            [
                NotYetClassifiedElement(html_tag("p")),
                TopLevelSectionTitle(html_tag("p")),
                NotYetClassifiedElement(html_tag("p")),
                TopLevelSectionTitle(html_tag("p")),
                NotYetClassifiedElement(html_tag("p")),
            ],
            [
                {"type": TopLevelSectionTitle, "tag": "p"},
                {"type": NotYetClassifiedElement, "tag": "p"},
                {"type": TopLevelSectionTitle, "tag": "p"},
                {"type": NotYetClassifiedElement, "tag": "p"},
            ],
        ),
    ],
)
def test_pre_top_level_section_pruner(elements, expected_elements):
    # Arrange
    step = PreTopLevelSectionPruner()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
