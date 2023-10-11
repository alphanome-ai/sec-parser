from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:
    from sec_parser.processing_engine.html_tag import HtmlTag


class CompositeSemanticElement(AbstractSemanticElement):
    """
    CompositeSemanticElement acts as a container that can encapsulate other
    semantic elements.

    This is used for handling special cases where a single HTML root
    tag wraps multiple semantic elements. This maintains structural integrity
    and allows for seamless reconstitution of the original HTML document.

    Why is this useful:
    ===================
    1. Some semantic elements, like XBRL tags (<ix>), may wrap multiple semantic
    elements. The container ensures that these relationships are not broken
    during parsing.
    2. Enables the parser to fully reconstruct the original HTML document, which
    opens up possibilities for features like semantic segmentation visualization
    (e.g. recreate the original document but put semi-transparent colored boxes
    on top, based on semantic meaning), serialization of parsed documents into
    an augmented HTML, and debugging by comparing to the original document.
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        inner_elements: list[AbstractSemanticElement] | None,
    ) -> None:
        super().__init__(html_tag)
        if inner_elements is None:
            msg = "inner_elements cannot be None."
            raise ValueError(msg)
        self._inner_elements: list[AbstractSemanticElement] = []
        self.inner_elements = inner_elements  # call 'inner_elements` setter

    @property
    def inner_elements(self) -> list[AbstractSemanticElement]:
        return self._inner_elements.copy()

    @inner_elements.setter
    def inner_elements(self, elements: list[AbstractSemanticElement]) -> None:
        if not elements:
            msg = "inner_elements cannot be empty."
            raise ValueError(msg)
        self._inner_elements = elements

    @classmethod
    def convert_from(
        cls,
        source: AbstractSemanticElement,
        *,
        inner_elements: list[AbstractSemanticElement] | None = None,
    ) -> CompositeSemanticElement:
        return cls(
            html_tag=source.html_tag,
            inner_elements=inner_elements,
        )
