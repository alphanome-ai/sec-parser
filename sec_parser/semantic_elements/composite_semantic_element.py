from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sec_parser.exceptions import SecParserValueError
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

    from sec_parser.processing_engine.html_tag import HtmlTag
    from sec_parser.processing_engine.processing_log import LogItemOrigin, ProcessingLog


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
        inner_elements: tuple[
            AbstractSemanticElement,
            ...,
        ]
        | None,
        *,
        processing_log: ProcessingLog | None = None,
        log_origin: LogItemOrigin | None = None,
    ) -> None:
        super().__init__(html_tag, processing_log=processing_log, log_origin=None)
        self._inner_elements: tuple[AbstractSemanticElement, ...] = ()
        if not inner_elements:
            msg = "inner_elements cannot be None or empty."
            raise SecParserValueError(msg)
        self.inner_elements = inner_elements
        self.log_init(log_origin)

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
            raise SecParserValueError(msg)
        self._inner_elements = elements

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        log_origin: LogItemOrigin,
        *,
        inner_elements: list[AbstractSemanticElement] | None = None,
    ) -> CompositeSemanticElement:
        return cls(
            source.html_tag,
            log_origin=log_origin,
            processing_log=source.processing_log,
            inner_elements=tuple(inner_elements) if inner_elements else None,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "inner_elements": len(self.inner_elements),
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
