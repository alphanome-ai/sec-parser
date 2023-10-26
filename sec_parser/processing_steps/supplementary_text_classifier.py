from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.highlighted_text_element import HighlightedTextElement
from sec_parser.semantic_elements.semantic_elements import (
    SupplementaryText,
    TextElement,
)
from sec_parser.utils.py_utils import clean_whitespace

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class SupplementaryTextClassifier(AbstractElementwiseProcessingStep):
    """
    SupplementaryTextClassifier class for converting elements into
    SupplementaryText instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with SupplementaryText instances.
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
        is_text = isinstance(element, TextElement)
        is_highlighted_text = isinstance(element, HighlightedTextElement)
        if not is_text and not is_highlighted_text:
            return element

        if element.text.startswith("(") and element.text.endswith(")"):
            return SupplementaryText.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )
        if (
            isinstance(element, HighlightedTextElement)
            and element.style.italic
            and element.text.endswith(".")
        ):
            return SupplementaryText.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )
        normalized_text = clean_whitespace(element.text).lower()
        if (
            (
                (
                    "notes" in normalized_text
                    and "financial statements" in normalized_text
                )
                or "accompanying notes" in normalized_text
            )
            and normalized_text.count(".") == 1
            and normalized_text.endswith(".")
        ):
            return SupplementaryText.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )
        return element
