from __future__ import annotations

from typing import TYPE_CHECKING, Any

from frozendict import frozendict

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

    from sec_parser.processing_engine.html_tag import HtmlTag


class CompositeSemanticElement(AbstractSemanticElement):
    """
    CompositeSemanticElement acts as a container for other semantic elements,
    especially for cases where a single HTML root tag wraps multiple elements.
    This ensures structural integrity and enables various features like
    semantic segmentation visualization, and debugging by comparison with the
    original document.

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
        transformation_history: tuple[
            AbstractSemanticElement,
            ...,
        ],
        inner_elements: tuple[
            AbstractSemanticElement,
            ...,
        ]
        | None,
        composite_element_reasons: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(html_tag, transformation_history)

        self._inner_elements: tuple[AbstractSemanticElement, ...] = ()
        if not inner_elements:
            msg = "inner_elements cannot be None or empty."
            raise ValueError(msg)
        for element in inner_elements:
            element.append_to_transformation_history(self)
        self.inner_elements = inner_elements

        self.composite_element_reasons: frozendict[str, Any] = frozendict(
            composite_element_reasons or {},
        )

    @property
    def inner_elements(
        self,
    ) -> tuple[AbstractSemanticElement, ...]:
        return self._inner_elements

    @inner_elements.setter
    def inner_elements(
        self,
        elements: tuple[AbstractSemanticElement, ...] | None,
    ) -> None:
        if not elements:
            msg = "inner_elements cannot be None or empty."
            raise ValueError(msg)
        for element in elements:
            if not any(
                isinstance(e, CompositeSemanticElement)
                for e in element.get_transformation_history()
            ):
                msg = (
                    "Transformation history does not contain an"
                    " instance of CompositeSemanticElement."
                )
                raise ValueError(msg)
        self._inner_elements = elements

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        *,
        inner_elements: list[AbstractSemanticElement] | None = None,
        composite_element_reasons: dict[str, Any] | None = None,
    ) -> CompositeSemanticElement:
        return cls(
            source.html_tag,
            source.get_transformation_history(),
            tuple(inner_elements) if inner_elements else None,
            composite_element_reasons,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "inner_elements": len(self.inner_elements),
            "composite_element_reasons": self.composite_element_reasons,
        }

    @classmethod
    def unwrap_elements(
        cls,
        elements: Iterable[AbstractSemanticElement],
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
        return flattened_elements
