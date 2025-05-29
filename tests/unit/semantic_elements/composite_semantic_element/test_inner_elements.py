import bs4
import pytest

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement


def test_inner_elements_setter() -> None:
    # Arrange
    tag = bs4.Tag(name="span")
    tag.string = "A" * 60
    element = CompositeSemanticElement(
        HtmlTag(tag),
        inner_elements=(
            NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p"))),
            NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p"))),
        ),
    )

    # Act & Assert
    with pytest.raises(SecParserValueError):
        element.inner_elements = None
