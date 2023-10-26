from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TopLevelSectionTitleClassifier(AbstractElementwiseProcessingStep):
    """
    TableClassifier class for inserting TopLevelSectionStartMarker elements
    into the list of elements. This step scans through a list of semantic
    elements and changes it.
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
        self._last_part: str = "?"

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        text = _normalize_string(element.text)
        if match := re.search(r"^part (i+)", text):
            self._last_part = str(len(match.group(1)))
            return TopLevelSectionTitle.create_from_element(
                element,
                level=0,
                identifier=f"part{self._last_part}",
                log_origin=self.__class__.__name__,
            )
        if match := re.search(r"^item (\d+a?)", text):
            item = match.group(1)
            return TopLevelSectionTitle.create_from_element(
                element,
                level=1,
                identifier=f"part{self._last_part}item{item}",
                log_origin=self.__class__.__name__,
            )
        return element


def _normalize_string(input_str: str) -> str:
    input_str = input_str.lower()
    # Remove all characters that are not a-z, 0-9, or whitespace
    input_str = re.sub(r"[^a-z0-9\s]", "", input_str)
    # Replace multiple whitespaces with a single space
    input_str = re.sub(r"\s+", " ", input_str)
    return input_str.strip()
