from sec_parser.exceptions.core_exceptions import SecParserValueError
from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag
from sec_parser.semantic_elements.base_semantic_element import (
    BaseSemanticElement,
)


class UndeterminedElement(BaseSemanticElement):
    """
    The UndeterminedElement class represents an element whose type
    has not yet been determined. The parsing process aims to
    transform all instances of this class into more specific
    subclasses of AbstractSemanticElement.
    """


class RootSectionElement(BaseSemanticElement):
    """
    The RootSectionElement class represents the top-level section of a document.
    For instance, in SEC 10-Q reports, a RootSection could be "Part I, Item 3.
    Quantitative and Qualitative Disclosures About Market Risk.".
    """


class TitleElement(BaseSemanticElement):
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


class TextElement(BaseSemanticElement):
    """The TextElement class represents a standard text paragraph within a document."""


class IrrelevantElement(BaseSemanticElement):
    """
    The IrrelevantElement class identifies elements in the parsed HTML that do not
    contribute to the content. These elements often include page separators, page
    numbers, and other non-content items. For instance, HTML tags without content
    like <p></p> or <div></div> are deemed irrelevant, often used in documents just
    to add vertical space.
    """
