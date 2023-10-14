from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
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
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        *,
        inner_elements: list[AbstractSemanticElement] | None = None,
    ) -> CompositeSemanticElement:
        return cls(
            html_tag=source.html_tag,
            inner_elements=inner_elements,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "inner_elements": len(self.inner_elements),
        }

    @classmethod
    def unwrap_elements(
        cls,
        elements: list[AbstractSemanticElement],
        *,
        include_containers: bool | None = None,
    ) -> list[AbstractSemanticElement]:
        """
        Recursively flatten a list of AbstractSemanticElement objects.
        For each CompositeSemanticElement encountered, its inner_elements
        are also recursively flattened. The 'include_containers' parameter controls
        whether the CompositeSemanticElement itself is included in the flattened list.
        """
        include_containers = False if include_containers is None else include_containers
        flattened_elements = []
        for e in elements:
            if not isinstance(e, CompositeSemanticElement):
                flattened_elements.append(e)
                continue

            if include_containers:
                flattened_elements.append(e)
            flattened_elements.extend(
                cls.unwrap_elements(
                    e.inner_elements,
                    include_containers=include_containers,
                ),
            )
        return flattened_elements
