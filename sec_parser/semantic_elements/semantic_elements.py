from __future__ import annotations

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)


class NotYetClassifiedElement(AbstractSemanticElement):
    """
    The NotYetClassifiedElement class represents an element whose type
    has not yet been determined. The parsing process aims to
    classify all instances of this class into more specific
    subclasses of AbstractSemanticElement.
    """


class TopLevelSectionStartMarker(AbstractSemanticElement):
    """
    The TopLevelSectionStartMarker class represents the beginning of a top-level
    section of a document. For instance, in SEC 10-Q reports, a
    top-level section could be "Part I, Item 3. Quantitative and Qualitative
    Disclosures About Market Risk.".
    """


class IrrelevantElement(AbstractSemanticElement):
    """
    The IrrelevantElement class identifies elements in the parsed HTML that do not
    contribute to the content. These elements often include page separators, page
    numbers, and other non-content items. For instance, HTML tags without content
    like <p></p> or <div></div> are deemed irrelevant, often used in documents just
    to add vertical space.
    """


class EmptyElement(AbstractSemanticElement):
    """
    The EmptyElement class represents an HTML element that does not contain any content.
    It is a subclass of the IrrelevantElement class and is used to identify and handle
    empty HTML tags in the document.
    """


class TitleElement(AbstractLevelElement, AbstractSemanticElement):
    """
    The TitleElement class represents the title of a paragraph or other content object.
    It serves as a semantic marker, providing context and structure to the document.
    """


class TextElement(AbstractSemanticElement):
    """The TextElement class represents a standard text paragraph within a document."""


class ImageElement(AbstractSemanticElement):
    """The ImageElement class represents a standard image within a document."""
