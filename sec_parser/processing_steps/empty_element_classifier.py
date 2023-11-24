from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )
    from sec_parser.semantic_elements.title_element import TitleElement


class InvalidIterationError(ValueError):
    """Raised when an invalid iteration value is encountered."""


class EmptyElementClassifier(AbstractElementwiseProcessingStep):
    """
    IrrelevantElementClassifier class for converting elements
    into IrrelevantElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with IrrelevantElement instances.
    """

    _NUM_ITERATIONS = 1

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

        # Text duplicate finder
        self._text_occurences: Counter[str] = Counter()
        self._min_occurences_to_classify_as_irrelevant = 10

        # Finding a company name element that precedes other titles
        self._previous_title: TitleElement | None = None
        self._consecutive_title_and_level_occurences: Counter[str] = Counter()
        self._min_title_occurences_to_classify_as_irrelevant = 2

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        """
        Transform a single semantic element
        into a IrrelevantElement if applicable.
        """
        if not element.contains_words():
            element.processing_log.add_item(
                message="Does not contain words",
                log_origin=self.__class__.__name__,
            )
            return EmptyElement.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )
        return element
