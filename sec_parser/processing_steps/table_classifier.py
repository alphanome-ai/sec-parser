from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.table_element import TableElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TableClassifier(AbstractElementwiseProcessingStep):
    """
    TableClassifier class for converting elements into TableElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TableElement instances.
    """

    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__()
        self._types_to_process = types_to_process or set()
        self._types_to_exclude = types_to_exclude or set()
        self._row_count_threshold = 1

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        is_unary = element.html_tag.is_unary_tree()
        contains_table = element.html_tag.contains_tag("table", include_self=True)
        if is_unary and contains_table:
            metrics = element.html_tag.get_approx_table_metrics()
            if metrics.rows > self._row_count_threshold:
                return TableElement.create_from_element(element)

        return element
