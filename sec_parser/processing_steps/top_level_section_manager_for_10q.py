from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from sec_parser.semantic_elements.top_level_section_title_types import (
    IDENTIFIER_TO_10Q_SECTION,
    TopLevelSectionType,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


part_pattern = re.compile(r"^part\s+(i+)", re.IGNORECASE)
item_pattern = re.compile(r"^item\s+(\d+a?)", re.IGNORECASE)


@dataclass
class _Candidate:
    section_type: TopLevelSectionType
    element: AbstractSemanticElement


class TopLevelSectionManagerFor10Q(AbstractElementwiseProcessingStep):
    """
    Documents are divided into sections, subsections, and so on.
    Top level sections are the highest level of sections and are
    standardized across each type of document.

    An example of a Top Level Section in a 10-Q report is
    "Part I, Item 3. Quantitative and Qualitative
    Disclosures About Market Risk.".
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
        self._candidates: list[_Candidate] = []
        self._selected_candidates: tuple[_Candidate, ...] | None = None
        self._last_part: str = "?"

    @staticmethod
    def match_part(text: str) -> str | None:
        if match := part_pattern.search(text):
            return str(len(match.group(1)))
        return None

    @staticmethod
    def match_item(text: str) -> str | None:
        if match := item_pattern.search(text):
            return match.group(1).lower()
        return None

    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        if context.iteration == 0:
            candidate = None

            if part := self.match_part(element.text):
                self._last_part = part
                section_type = IDENTIFIER_TO_10Q_SECTION[f"part{self._last_part}"]
                candidate = _Candidate(section_type, element)
            elif item := self.match_item(element.text):
                section_type = IDENTIFIER_TO_10Q_SECTION[
                    f"part{self._last_part}item{item}"
                ]
                candidate = _Candidate(section_type, element)

            if candidate is not None:
                self._candidates.append(candidate)
                element.processing_log.add_item(
                    message=f"Identified as candidate: {candidate.section_type.identifier}",
                    log_origin=self.__class__.__name__,
                )
            return element
        if context.iteration == 1:
            if self._selected_candidates is None:
                grouped_candidates: dict[
                    TopLevelSectionType,
                    list[AbstractSemanticElement],
                ] = defaultdict(list)
                for candidate in self._candidates:
                    grouped_candidates[candidate.section_type].append(candidate.element)

                # Last candidate is the most likely to be the correct one
                self._selected_candidates = tuple(
                    _Candidate(section_type=section_type, element=element[-1])
                    for section_type, element in grouped_candidates.items()
                )

            for candidate in self._selected_candidates:
                if candidate.element is element:
                    return TopLevelSectionTitle.create_from_element(
                        candidate.element,
                        level=candidate.section_type.level,
                        section_type=candidate.section_type,
                        log_origin=self.__class__.__name__,
                    )
            return element
        msg = f"Invalid iteration: {context.iteration}"
        raise ValueError(msg)
