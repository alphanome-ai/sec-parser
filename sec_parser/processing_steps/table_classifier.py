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
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )
        self._row_count_threshold = 1

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        if element.html_tag.contains_tag("table", include_self=True):
            metrics = element.html_tag.get_approx_table_metrics()
            if metrics.rows > self._row_count_threshold:
                return TableElement.create_from_element(
                    element,
                    log_origin=self.__class__.__name__,
                )
            element.processing_log.add_item(
                log_origin=self.__class__.__name__,
                message=(
                    f"Skipping: Table has {metrics.rows} rows, which is below the "
                    f"threshold of {self._row_count_threshold}."
                ),
            )
        return element

    @classmethod
    def contains_single_element(cls, element: AbstractSemanticElement) -> bool | None:
        el_tag = element.html_tag
        if el_tag.name == "table":
            return True

        table_count = el_tag.count_tags("table")

        if table_count > 1:
            msg = f"Detected multiple <table> tags ({table_count})"
            element.processing_log.add_item(
                log_origin=cls.__name__,
                message=msg,
            )
            return False

        if table_count == 1 and el_tag.has_text_outside_tags("table"):
            element.processing_log.add_item(
                log_origin=cls.__name__,
                message="Detected text outside of the <table> tag.",
            )
            return False

        return None
