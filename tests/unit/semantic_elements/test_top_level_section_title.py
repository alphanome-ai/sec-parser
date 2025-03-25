import bs4

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.highlighted_text_element import TextStyle
from sec_parser.semantic_elements.top_section_title import TopSectionTitle
from sec_parser.semantic_elements.top_section_title_types import (
    FilingSectionsIn10Q,
)


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    identifier = "part1item2"
    section_type = FilingSectionsIn10Q.identifier_to_section[identifier]

    # Act
    actual = TopSectionTitle(HtmlTag(tag), section_type=section_type).to_dict(
        include_previews=True,
    )

    # Assert
    assert actual["section_type"] == identifier
