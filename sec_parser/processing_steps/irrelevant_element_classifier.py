from __future__ import annotations

import re
from collections import Counter
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    IrrelevantElement,
)
from sec_parser.semantic_elements.title_element import TitleElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class InvalidIterationError(ValueError):
    """Raised when an invalid iteration value is encountered."""


class IrrelevantElementClassifier(AbstractElementwiseProcessingStep):
    """
    IrrelevantElementClassifier class for converting elements
    into IrrelevantElement instances.

    This step scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with IrrelevantElement instances.
    """

    _NUM_ITERATIONS = 2

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
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        """
        Transform a single semantic element
        into a IrrelevantElement if applicable.
        """
        if context.iteration == 0:
            return self._step1(element)
        if context.iteration == 1:
            return self._step2(element)

        msg = f"Invalid iteration: {context.iteration}"
        raise InvalidIterationError(msg)

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\b\d+\b", " ", text).lower()

    def _step1(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        if not element.contains_words():
            element.processing_log.add_item(
                message="Does not contain words",
                log_origin=self.__class__.__name__,
            )
            return EmptyElement.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )

        # Text duplicate finder
        normalized_text = self._normalize_text(element.text)
        skip_keywords = ["continued", "unaudited"]
        if not any(keyword in normalized_text for keyword in skip_keywords):
            self._text_occurences[normalized_text] += 1

        # Finding a company name element that precedes other titles
        if isinstance(element, TitleElement):
            if self._previous_title is not None:
                self._consecutive_title_and_level_occurences[
                    self._previous_title.text
                ] += 1
            self._previous_title = element
        else:
            self._previous_title = None

        return element

    def _step2(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        if isinstance(element, EmptyElement):
            return element

        # Text duplicate pruner
        if (
            self._text_occurences[self._normalize_text(element.text)]
            >= self._min_occurences_to_classify_as_irrelevant
        ):
            element.processing_log.add_item(
                message=f"Text duplicates at least {self._min_occurences_to_classify_as_irrelevant} times",
                log_origin=self.__class__.__name__,
            )
            return IrrelevantElement.create_from_element(
                element,
                log_origin=self.__class__.__name__,
            )

        # Consecutive irrelevant title (of same level) pruner
        if self._consecutive_title_and_level_occurences:
            max_occurrences = max(self._consecutive_title_and_level_occurences.values())
            if isinstance(element, TitleElement) and (
                self._consecutive_title_and_level_occurences[element.text]
                >= self._min_title_occurences_to_classify_as_irrelevant
                and self._text_occurences[self._normalize_text(element.text)]
                == max_occurrences
            ):
                element.processing_log.add_item(
                    message=f"Consecutive irrelevant title (of same level) at least {self._min_title_occurences_to_classify_as_irrelevant} times",
                    log_origin=self.__class__.__name__,
                )
                return IrrelevantElement.create_from_element(
                    element,
                    log_origin=self.__class__.__name__,
                )

        return element
