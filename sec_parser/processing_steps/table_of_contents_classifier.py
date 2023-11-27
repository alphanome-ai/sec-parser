from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.table_element.table_of_contents_element import (
    TableOfContentsElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TableOfContentsClassifier(AbstractElementwiseProcessingStep):
    """
    TableOfContentsClassifier class for converting elements into TableOfContentsElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TableOfContentsElement instances.
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

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        is_table_of_content=element.html_tag.is_table_of_content()

        if is_table_of_content is True:
            return TableOfContentsElement.create_from_element(
            element,
            log_origin=self.__class__.__name__,
            )

        return element
