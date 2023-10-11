from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    BulletpointTextElement,
    FootnoteTextElement,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class FootnoteAndBulletpointParsingStep(AbstractElementwiseProcessStep):
    """
    FootnoteAndBulletpointParsingStep class for transforming elements into
    BulletpointTextElement and FootnoteTextElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with
    BulletpointElement and FootnoteTextElement instances.
    """

    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )

        # _unique_markers_by_order track unique symbols in the document.
        # Stored in a tuple as an ordered set, preserving insertion order.
        # This order is used to determine a bulletpoint's level.
        # It makes use of the fact that "higher level" markers appear
        # first in the document.
        # _unique_markers_by_order is effectively used as an ordered set:
        self._unique_markers_by_order: tuple[str, ...] = ()

    def _add_unique_marker(self, symbol: str) -> None:
        if symbol not in self._unique_markers_by_order:
            # _unique_markers_by_order is effectively updated as an ordered set:
            self._unique_markers_by_order = tuple(
                dict.fromkeys([*self._unique_markers_by_order, symbol]).keys(),
            )

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        deepest_tag = element.html_tag.get_first_deepest_tag()
        if not deepest_tag:
            return element

        marker = deepest_tag.get_text()
        if not marker:
            return element

        if marker.replace(".", "").isdigit():
            return FootnoteTextElement.convert_from(element)

        if len(marker) == 1:
            self._add_unique_marker(marker)
            level = 1 + self._unique_markers_by_order.index(marker)
            return BulletpointTextElement(
                element.html_tag,
                element.inner_elements,
                level=level,
            )

        return element
