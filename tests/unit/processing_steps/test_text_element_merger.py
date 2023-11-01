import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.text_element_merger import TextElementMerger
from sec_parser.semantic_elements.semantic_elements import (
    AbstractSemanticElement,
    TextElement,
)
from tests.unit._utils import assert_elements


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


@pytest.mark.parametrize(
    ("name", "elements", "expected_elements"),
    values := [
        (
            "no_merge_single_text_element",
            [
                TextElement(html_tag("span", text="Hello World.")),
            ],
            [
                {
                    "type": TextElement,
                    "tag": "span",
                    "text": "Hello World.",
                },
            ],
        ),
        (
            "merge_adjacent_text_elements",
            [
                TextElement(html_tag("span", text="Text 1.")),
                TextElement(html_tag("span", text="Text 2.")),
                TextElement(html_tag("span", text="Text 3.")),
            ],
            [
                {
                    "type": TextElement,
                    "tag": "sec-parser-merged-text",
                    "text": "Text 1.Text 2.Text 3.",
                },
            ],
        ),
        (
            "no_merge_other_elements",
            [
                TextElement(html_tag("span", text="Text 1.")),
                AbstractSemanticElement(html_tag("div", text="Middle Divider.")),
                TextElement(html_tag("span", text="Text 2.")),
            ],
            [
                {
                    "type": TextElement,
                    "tag": "span",
                    "text": "Text 1.",
                },
                {
                    "type": AbstractSemanticElement,
                    "tag": "div",
                    "text": "Middle Divider.",
                },
                {
                    "type": TextElement,
                    "tag": "span",
                    "text": "Text 2.",
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_merge_text_elements(name, elements, expected_elements):
    # Arrange
    step = TextElementMerger()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
