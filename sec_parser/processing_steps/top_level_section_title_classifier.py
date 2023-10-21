from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    TitleElement,
    TopLevelSectionTitle,
)

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

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        if not isinstance(element, TitleElement):
            return element
        text = _normalize_string(element.text)
        if re.search(r"^part i+", text):
            return TopLevelSectionTitle.create_from_element(element, level=0)
        if re.search(r"^item \d+a?", text):
            return TopLevelSectionTitle.create_from_element(element, level=1)
        return element


def _normalize_string(input_str: str) -> str:
    input_str = input_str.lower()
    # Remove all characters that are not a-z, 0-9, or whitespace
    input_str = re.sub(r"[^a-z0-9\s]", "", input_str)
    # Replace multiple whitespaces with a single space
    input_str = re.sub(r"\s+", " ", input_str)
    return input_str.strip()
