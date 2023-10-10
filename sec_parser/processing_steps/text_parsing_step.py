from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseTransformStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import EmptyElement, TextElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TextParsingStep(AbstractElementwiseTransformStep):
    """
    TextParsingStep class for transforming elements into TextElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TextElement instances.
    """

    def __init__(
        self,
        *,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            process_only=process_only,
            except_dont_process=except_dont_process,
        )
        self._unique_markers_by_order: list[str] = []

    def _found_marker(self, symbol: str) -> None:
        if symbol not in self._unique_markers_by_order:
            # Ordered set:
            self._unique_markers_by_order = list(
                dict.fromkeys([*self._unique_markers_by_order, symbol]).keys(),
            )

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        """
        Transform a single semantic element
        into a TextElement if applicable.
        """
        if element.html_tag.get_text() == "":
            return EmptyElement.convert_from(element)
        return TextElement.convert_from(element)
