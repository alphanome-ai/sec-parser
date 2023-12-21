from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import PageNumberElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


@dataclass(frozen=True)
class PageNumberCandidate:
    TEXT_LENGTH_THRESHOLD = 100
    OCCURRENCE_THRESHOLD = 5
    text: str


class MostCommonCandidateSearchStatus(Enum):
    NOT_SEARCHED = auto()
    NOT_EXIST = auto()
    FOUND = auto()


class PageNumberClassifier(AbstractElementwiseProcessingStep):
    _NUM_ITERATIONS = 2

    def __init__(
        self,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )
        self._element_to_page_number_candidate: dict[
            AbstractSemanticElement,
            PageNumberCandidate,
        ] = {}
        self._candidate_count: Counter[PageNumberCandidate] = Counter()
        self._most_common_candidate: PageNumberCandidate | None = None
        self._most_common_candidate_count: int = 0
        self._search_status: MostCommonCandidateSearchStatus = (
            MostCommonCandidateSearchStatus.NOT_SEARCHED
        )

    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        if context.iteration == 0:
            self._find_page_number_candidates(element)
            return element
        if context.iteration == 1:
            return self._classify_elements(element)
        msg = f"Invalid iteration: {context.iteration}"
        raise ValueError(msg)

    def _find_page_number_candidates(self, element: AbstractSemanticElement) -> None:
        if len(element.text) > PageNumberCandidate.TEXT_LENGTH_THRESHOLD:
            return
        if not any(char.isdigit() for char in element.text):
            return
        text_without_digits = "".join(c for c in element.text if not c.isdigit())
        if element.text == text_without_digits:
            return

        element.processing_log.add_item(
            message="Identified as a page number candidate.",
            log_origin=self.__class__.__name__,
        )
        candidate = PageNumberCandidate(text_without_digits)
        self._element_to_page_number_candidate[element] = candidate
        self._candidate_count[candidate] += 1

    def _classify_elements(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        most_common_candidate = self._get_most_common_candidate()
        if most_common_candidate is None:
            return element
        candidate = self._element_to_page_number_candidate.get(element)
        if candidate != self._most_common_candidate:
            return element

        element.processing_log.add_item(
            message=f"Matches the most common (x{self._most_common_candidate_count}) candidate: {candidate}",
            log_origin=self.__class__.__name__,
        )
        return PageNumberElement.create_from_element(
            element,
            log_origin=self.__class__.__name__,
        )

    def _get_most_common_candidate(self) -> PageNumberCandidate | None:
        if self._search_status == MostCommonCandidateSearchStatus.NOT_SEARCHED:
            result = self._candidate_count.most_common(1)
            if not result:
                self._search_status = MostCommonCandidateSearchStatus.NOT_EXIST
                return None
            most_common_candidate, count = result[0]
            if count < PageNumberCandidate.OCCURRENCE_THRESHOLD:
                self._search_status = MostCommonCandidateSearchStatus.NOT_EXIST
                return None
            self._most_common_candidate = most_common_candidate
            self._most_common_candidate_count = count
            self._search_status = MostCommonCandidateSearchStatus.FOUND
        return self._most_common_candidate
