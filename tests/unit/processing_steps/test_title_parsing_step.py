from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.table_parsing_step import TableParsingStep
from sec_parser.processing_steps.title_parsing_step import TitleParsingStep
from sec_parser.semantic_elements.highlighted_text_element import (
    HighlightedTextElement,
    TextStyle,
)
from sec_parser.semantic_elements.semantic_elements import TableElement, TitleElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


bold = TextStyle(
    bold_with_font_weight=True,
    italic=False,
)
italic = TextStyle(
    bold_with_font_weight=False,
    italic=True,
)


@pytest.mark.parametrize(
    ("elements", "expected_elements"),
    [
        (
            [
                HighlightedTextElement(html_tag("p"), style=italic),
                HighlightedTextElement(html_tag("p"), style=bold),
                HighlightedTextElement(html_tag("p"), style=bold),
                HighlightedTextElement(html_tag("p"), style=italic),
            ],
            [
                {"type": TitleElement, "tag": "p", "fields": {"level": 0}},
                {"type": TitleElement, "tag": "p", "fields": {"level": 1}},
                {"type": TitleElement, "tag": "p", "fields": {"level": 1}},
                {"type": TitleElement, "tag": "p", "fields": {"level": 0}},
            ],
        ),
    ],
)
def test_title_parsing_step(elements, expected_elements):
    # Arrange
    step = TitleParsingStep()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
