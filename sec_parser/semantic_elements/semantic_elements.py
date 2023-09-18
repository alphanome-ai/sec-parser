from sec_parser.exceptions.core_exceptions import SecParserValueError
from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class UndeterminedElement(AbstractSemanticElement):
    """
    The UndeterminedElement class represents an element whose type
    has not yet been determined. The parsing process aims to
    transform all instances of this class into more specific
    subclasses of AbstractSemanticElement.
    """


class RootSectionElement(AbstractSemanticElement):
    """
    The RootSectionElement class represents the top-level section of a document.
    For instance, in SEC 10-Q reports, a RootSection could be "Part I, Item 3.
    Quantitative and Qualitative Disclosures About Market Risk.".
    """


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


class RootSectionSeparatorElement(IrrelevantElement):
    """
    The RootSectionSeparatorElement class represents a tag <document-root-section>,
    or any tag that contains it.

    We're currently using *sec-api.io* to handle the removal of the
    title 10-Q page and to download 10-Q Section HTML files. The sections
    are then joined by inserting a <document-root-section> separator. In the
    future, we aim to download these HTML files directly from the SEC EDGAR.
    """


class HighlightedElement(AbstractSemanticElement):
    """
    The HighlightedElement class used for detecting title elements.
    The process begins with the detection of highlighted elements,
    which are then further classified into title elements.
    """


class TitleElement(AbstractSemanticElement):
    """
    The TitleElement class represents the title of a paragraph or other content object.
    It serves as a semantic marker, providing context and structure to the document.
    """

    MIN_LEVEL = 1

    def __init__(self, html_tag: HtmlTag, *, level: int = MIN_LEVEL) -> None:
        super().__init__(html_tag)

        if level < self.MIN_LEVEL:
            msg = f"Level must be equal or greater than {self.MIN_LEVEL}"
            raise InvalidTitleLevelError(msg)
        self.level = level


class InvalidTitleLevelError(SecParserValueError):
    pass


class TextElement(AbstractSemanticElement):
    """The TextElement class represents a standard text paragraph within a document."""


class TableElement(AbstractSemanticElement):
    """The TableElement class represents a standard table within a document."""


class ImageElement(AbstractSemanticElement):
    """The ImageElement class represents a standard image within a document."""
