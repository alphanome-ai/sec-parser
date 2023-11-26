from __future__ import annotations

import re
import warnings
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
    InvalidTopLevelSectionIn10Q,
    TopLevelSectionType,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


part_pattern = re.compile(r"part\s+(i+)[.\s]*", re.IGNORECASE)
item_pattern = re.compile(r"item\s+(\d+a?)[.\s]*", re.IGNORECASE)


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
        self._last_order_number = float("-inf")

    @classmethod
    def is_match_part_or_item(cls, text: str) -> bool:
        part_match = cls.match_part(text) is not None
        item_match = cls.match_item(text) is not None
        return part_match or item_match

    @staticmethod
    def match_part(text: str) -> str | None:
        if match := part_pattern.match(text):
            return str(len(match.group(1)))
        return None

    @staticmethod
    def match_item(text: str) -> str | None:
        if match := item_pattern.match(text):
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
                section_type = IDENTIFIER_TO_10Q_SECTION.get(
                    f"part{self._last_part}",
                    InvalidTopLevelSectionIn10Q,
                )
                if section_type is InvalidTopLevelSectionIn10Q:
                    warnings.warn(
                        f"Invalid section type for part{self._last_part}. Defaulting to InvalidTopLevelSectionIn10Q.",
                        UserWarning,
                        stacklevel=8,
                    )
                candidate = _Candidate(section_type, element)
            elif item := self.match_item(element.text):
                section_type = IDENTIFIER_TO_10Q_SECTION.get(
                    f"part{self._last_part}item{item}",
                    InvalidTopLevelSectionIn10Q,
                )
                if section_type is InvalidTopLevelSectionIn10Q:
                    warnings.warn(
                        f"Invalid section type for part{self._last_part}item{item}. Defaulting to InvalidTopLevelSectionIn10Q.",
                        UserWarning,
                        stacklevel=8,
                    )
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

                def select_element(
                    elements: list[AbstractSemanticElement],
                ) -> AbstractSemanticElement:
                    if len(elements) == 1:
                        return elements[0]
                    elements_without_table = [
                        element
                        for element in elements
                        if not element.html_tag.contains_tag("table", include_self=True)
                    ]
                    if len(elements_without_table) >= 1:
                        return elements_without_table[0]
                    return elements[0]

                self._selected_candidates = tuple(
                    _Candidate(
                        section_type=section_type,
                        element=select_element(element),
                    )
                    for section_type, element in grouped_candidates.items()
                )

            for candidate in self._selected_candidates:
                if candidate.element is element:
                    if candidate.section_type.order > self._last_order_number:
                        message = f"this.order={candidate.section_type.order} last_order_number={self._last_order_number}."
                        element.processing_log.add_item(
                            message=message,
                            log_origin=self.__class__.__name__,
                        )
                        self._last_order_number = candidate.section_type.order
                    else:
                        message = (
                            f"Order number {candidate.section_type.order} is not greater "
                            f"than last order number {self._last_order_number}."
                        )
                        element.processing_log.add_item(
                            message=message,
                            log_origin=self.__class__.__name__,
                        )
                        continue
                    return TopLevelSectionTitle.create_from_element(
                        candidate.element,
                        level=candidate.section_type.level,
                        section_type=candidate.section_type,
                        log_origin=self.__class__.__name__,
                    )
            return element
        msg = f"Invalid iteration: {context.iteration}"
        raise ValueError(msg)
