import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.pre_top_level_section_pruner import (
    PreTopLevelSectionPruner,
)
from sec_parser.processing_steps.top_level_section_title_classifier import (
    TopLevelSectionTitleClassifier,
)
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
    TextElement,
    TitleElement,
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
                TextElement(html_tag("p", text="Item 1")),
                TextElement(html_tag("p", text="Part 1")),
                TitleElement(html_tag("p", text="Hello")),
                TitleElement(html_tag("p", text="Item 1")),
                TitleElement(html_tag("p", text="Part I")),
            ],
            [
                {"type": TextElement, "tag": "p"},
                {"type": TextElement, "tag": "p"},
                {"type": TitleElement, "tag": "p"},
                {"type": TopLevelSectionTitle, "tag": "p", "fields": {"level": 1}},
                {"type": TopLevelSectionTitle, "tag": "p", "fields": {"level": 0}},
            ],
        ),
    ],
)
def test_pre_top_level_section_pruner(elements, expected_elements):
    # Arrange
    step = TopLevelSectionTitleClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
