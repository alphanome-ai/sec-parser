from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_tag import HtmlTag


class AbstractSemanticElement:
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
