import bs4

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.highlighted_text_element import TextStyle
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from sec_parser.semantic_elements.top_level_section_title_types import (
    IDENTIFIER_TO_10Q_SECTION,
)


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    identifier = "part1item2"
    section_type = IDENTIFIER_TO_10Q_SECTION[identifier]

    # Act
    actual = TopLevelSectionTitle(HtmlTag(tag), section_type=section_type).to_dict()

    # Assert
    assert actual["section_type"] == identifier
