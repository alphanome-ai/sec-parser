from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag


class NotYetClassifiedElement(AbstractSemanticElement):
    """
    The NotYetClassifiedElement class represents an element whose type
    has not yet been determined. The parsing process aims to
    classify all instances of this class into more specific
    subclasses of AbstractSemanticElement.
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        transformation_history: tuple[AbstractSemanticElement, ...] = (),
    ) -> None:
        super().__init__(html_tag, transformation_history)


class IrrelevantElement(AbstractSemanticElement):
    """
    The IrrelevantElement class identifies elements in the parsed HTML that do not
    contribute to the content. These elements often include page separators, page
    numbers, and other non-content items. For instance, HTML tags without content
    like <p></p> or <div></div> are deemed irrelevant, often used in documents just
    to add vertical space.
    """


class EmptyElement(IrrelevantElement):
    """
    The EmptyElement class represents an HTML element that does not contain any content.
    It is a subclass of the IrrelevantElement class and is used to identify and handle
    empty HTML tags in the document.
    """


class TextElement(AbstractSemanticElement):
    """The TextElement class represents a standard text paragraph within a document."""


class SupplementaryText(AbstractSemanticElement):
    """
    The SupplementaryText class captures various types of supplementary text
    within a document, such as unit qualifiers, additional notes, and disclaimers.

    For example:
    - "(In millions, except number of shares which are reflected in thousands and
       per share amounts)"
    - "See accompanying Notes to Condensed Consolidated Financial Statements."
    - "Disclaimer: This is not financial advice."
    """


class ImageElement(AbstractSemanticElement):
    """The ImageElement class represents a standard image within a document."""
