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
from sec_parser.semantic_elements.top_section_title import TopSectionTitle
from sec_parser.semantic_elements.top_section_title_types import (
    IDENTIFIER_TO_10Q_SECTION,
    InvalidTopSectionIn10Q,
    TopSectionType,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


part_pattern = re.compile(r"part\s+(i+)[.\s]*", re.IGNORECASE)
item_pattern = re.compile(r"item\s+(\d+a?)[.\s]*", re.IGNORECASE)


@dataclass
class _Candidate:
    section_type: TopSectionType
    element: AbstractSemanticElement


class TopSectionManagerFor10Q(AbstractElementwiseProcessingStep):
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

    """
    Processes a single element during document parsing.

    Input:
    - element (type: AbstractSemanticElement): The semantic element to be processed.
    - context (type: ElementProcessingContext)

    Output:
    - element of type AbstractSemanticElement: the processed version (could have been converted) of the given semantic element "element".

    Raises:
    - ValueError: If the given iternation number is invalid. The allowed values of iteration numbers are 0 and 1.

    Functionality:
    - If the iteration number is 0:
       - Invokes the `_process_iteration_0` function.
       - Returns the element unchanged.

    - If the iteration number is 1:
       - Invokes the `_process_iteration_1` function.
       - Returns the value returned by `_process_iteration_1`.
    """
    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:

        if context.iteration == 0:
            self._process_iteration_0(element)
            return element


        if context.iteration == 1:
            return self._process_iteration_1(element)


        msg = f"Invalid iteration: {context.iteration}"
        raise ValueError(msg)

    """
    Calls the _identify_candidate function.
    Checks whether the given semantic element qualifies as a candidate or not.
    If it does, it appends the candidate version of the semantic element to the _candidates.
    """
    def _process_iteration_0(self, element: AbstractSemanticElement) -> None:
        self._identify_candidate(element)

    def _process_iteration_1(self, element: AbstractSemanticElement) -> AbstractSemanticElement:
        if self._selected_candidates is None:
            self._selected_candidates = self._select_candidates()

        return self._process_selected_candidates(element)

    """
    Input:
    - element (type: AbstractSemanticElement): The semantic element to be processed.

    Output:
    - No output

    Functionality:
    - Checks if the elements text matches a part pattern by calling the match_part method.
    - If the match_part returns a match, then it sets the matched text to the last_part variable.
    - Then identifies the section type and creates a candidate using the section type and the semantic element.
    - Else if checks whether the elements text matches an item pattern by calling the match_item method.
    - If the match_item returns a match, then it identifies the section type and creates a candidate using
      the section type and the semantic element.
    - Appends the identified candidate to the list of candidates "_candidates"
    """
    def _identify_candidate(self, element: AbstractSemanticElement) -> None:
        candidate = None

        if part := self.match_part(element.text):
            self._last_part = part
            section_type = self._get_section_type(f"part{self._last_part}")
            if section_type is InvalidTopSectionIn10Q:
                    warnings.warn(
                        f"Invalid section type for part{self._last_part}. Defaulting to InvalidTopSectionIn10Q.",
                        UserWarning,
                        stacklevel=8,
                    )
            candidate = _Candidate(section_type, element)
        elif item := self.match_item(element.text):
            section_type = self._get_section_type(f"part{self._last_part}item{item}")
            if section_type is InvalidTopSectionIn10Q:
                    warnings.warn(
                        f"Invalid section type for part{self._last_part}item{item}. Defaulting to InvalidTopSectionIn10Q.",
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

    """
    Returns the corresponding TopSectionType of the given identifier. The TopSectionType represents a standard top section type in the context of a 10-Q report.
    The function utilizes the IDENTIFIER_TO_10Q_SECTION dictionary.

    Input:
    - identifier (type: String): an identifier of a top section title expressed by a string

    Output:
    - returns the corresponding TopSectionType of the given identifier. Returns InvalisTopSectionIn10Q if the identifier doesn't match any TopSectionType.
    """
    def _get_section_type(self, identifier: str) -> TopSectionType:
        return IDENTIFIER_TO_10Q_SECTION.get(identifier, InvalidTopSectionIn10Q)

    """"
    Groups candidates by section type. Then selects the first element candidate of each section type by using the helper function select_element.

    Input: No input

    Output: returns a tuple of selected candidates. There should be a candidate for each section type.

    Enhancement: select_element can be omitted. It basically returns the first element.
    """
    def _select_candidates(self) -> tuple[_Candidate, ...]:
        grouped_candidates = defaultdict(list)
        for candidate in self._candidates:
            grouped_candidates[candidate.section_type].append(candidate.element)


        """
         Selects a semantic element from the provided list based on specific criteria.

         Input:
        - elements (type: a list of AbstractSemanticElement): instances of the AbstractSemanticElement class

         Output:
        - The selected AbstractSemanticElement.
        """
        def select_element(elements: list[AbstractSemanticElement]) -> AbstractSemanticElement:


            if len(elements) == 1:
                return elements[0]
            elements_without_table = [
                        element
                        for element in elements
                        if not element.html_tag.contains_tag("table", include_self = True)
                    ]
            if len(elements_without_table) >= 1:
                    return elements_without_table[0]
            return elements[0]


        return tuple(
            _Candidate(
                section_type=section_type,
                element=select_element(element),
            )
            for section_type, element in grouped_candidates.items()
        )

    """"
    Checks whether the given semantic element is in the selected candidates.
    If yes, it updates the last order number, in case the order of the candidate is greater than current last order number.
    Then it creates a top section title of the element and returns the new top section title element.

    If the given element is not in the selected candidates, it returns the element.

    Input:
    - element (type: AbstractSemanticElement): The semantic element to be processed.

    Output:
    - Either the original input element or a newly generated top section title element associated with the input element.
    """
    def _process_selected_candidates(self, element: AbstractSemanticElement) -> AbstractSemanticElement:


        if self._selected_candidates is None:
            return element


        for candidate in self._selected_candidates:
            if candidate.element is element:
                if candidate.section_type.order > self._last_order_number:
                    self._update_last_order_number(element, candidate.section_type.order)
                else:
                    self._log_order_number_not_greater(element, candidate.section_type.order)
                    continue
                return self._create_top_section_title(candidate)
        return element

    def _update_last_order_number(self, element: AbstractSemanticElement, order: float) -> None:
        message = f"this.order={order} last_order_number={self._last_order_number}."
        element.processing_log.add_item(
            message=message,
            log_origin=self.__class__.__name__,
        )
        self._last_order_number = order

    def _log_order_number_not_greater(self, element: AbstractSemanticElement, order: float) -> None:
        message = f"Order number {order} is not greater than last order number {self._last_order_number}."
        element.processing_log.add_item(
            message=message,
            log_origin=self.__class__.__name__,
        )

    def _create_top_section_title(
        self, candidate: _Candidate,
    ) -> AbstractSemanticElement:
        return TopSectionTitle.create_from_element(
            candidate.element,
            level=candidate.section_type.level,
            section_type=candidate.section_type,
            log_origin=self.__class__.__name__,
        )


"""
Algorithm:
1. Call process_element with semantic element and iteration context. The output should be the processed semantic element.
2. Process the semantic element based on the given iteration number.
3. If the iteration number is 0, then the process_iteration_0 identifies whether the given semantic element is a top section title canadidate
   And appends the element to the list of candidates if it qualifies as a top section title.
4. If the iteration number is 1, then it selects candidates for each section type. Then it processes the selected candidates.
   By iterating over all the selected candidates and checking whether the current semantic element is in the list of selected candidates.
   If yes, then it either updates last order number and creates a top section title element and returns it. or logs order number not greater and continues
   scanning the selected candidates.
   Returns the element unchanged

"""
"""
Algorithm Improved ChatGPT Version:
Begin by invoking the process_element function with a semantic element and the iteration context. Capture the output as the processed semantic element.

Proceed to process the semantic element based on the given iteration number.

If the iteration number is 0:
a. Utilize the process_iteration_0 function to determine if the semantic element qualifies as a top section title candidate.
b. If the element qualifies, append it to the list of candidates.

If the iteration number is 1:
a. Select candidates for each section type.
b. Process the selected candidates by iterating over them.
c. Check if the current semantic element is in the list of selected candidates.

If yes:
Update the last order number and returns the top section title element version of the current element
 or log the order number if it's not greater and continues to scan the list of selected candidates.
Return the element unchanged.
"""
