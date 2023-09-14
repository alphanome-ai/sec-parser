from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_tag import HtmlTag


class AbstractSemanticElement:
    """
    In the domain of HTML parsing, especially in the context of SEC EDGAR documents,
    a semantic element refers to a meaningful unit within the document that serves a
    specific purpose. For example, a paragraph or a table might be considered a
    semantic element. Unlike syntactic elements, which merely exist to structure the
    HTML, semantic elements carry information that is vital to the understanding of the
    document's content.

    This class serves as a foundational representation of such semantic elements,
    containing an HtmlTag object that stores the raw HTML tag information. Subclasses
    will implement additional behaviors based on the type of the semantic element.
    """

    def __init__(self: AbstractSemanticElement, html_tag: HtmlTag) -> None:
        self.html_tag = html_tag


class AbstractContainerElement(AbstractSemanticElement):
    def __init__(
        self: AbstractContainerElement,
        html_tag: HtmlTag,
        inner_elements: list[HtmlTag],
    ) -> None:
        self.html_tag = html_tag
        self.inner_elements = inner_elements
