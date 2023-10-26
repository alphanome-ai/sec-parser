from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import TextElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TextClassifier(AbstractElementwiseProcessingStep):
    """
    TextClassifier class for converting elements into TextElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TextElement instances.
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
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        """
        Transform a single semantic element
        into a TextElement if applicable.
        """
        if element.text != "":
            return TextElement.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )
        return element
