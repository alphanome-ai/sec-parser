import bs4

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    tag.string = "A" * 60

    # Act
    actual = CompositeSemanticElement(
        HtmlTag(tag),
        inner_elements=(
            NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p"))),
            NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p"))),
        ),
    ).to_dict(include_previews=True)

    # Assert
    assert actual["inner_elements"] == 2
