import bs4

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.highlighted_text_element import TextStyle
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    identifier = "foo"

    # Act
    actual = TopLevelSectionTitle(HtmlTag(tag), identifier=identifier).to_dict()

    # Assert
    assert actual["identifier"] == identifier
