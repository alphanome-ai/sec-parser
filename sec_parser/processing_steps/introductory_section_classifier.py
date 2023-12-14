from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.semantic_elements import IntroductorySectionElement
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class IntroductorySectionElementClassifier(AbstractElementwiseProcessingStep):
    """
    The IntroductorySectionElementClassifier is a processing step designed
    to classify elements that are located before the actual contents of
    the document.

    For example, consider a SEC EDGAR 10-Q report. This processing step
    will mark all elements that appear before the 'part1' section.
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
        self._part1_exists = False
        self._part1_found = False

    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        if context.iteration == 0:
            if (
                isinstance(element, TopLevelSectionTitle)
                and element.section_type.identifier == "part1"
            ):
                self._part1_exists = True
            return element
        if context.iteration == 1 and self._part1_exists:
            if (
                isinstance(element, TopLevelSectionTitle)
                and element.section_type.identifier == "part1"
            ):
                self._part1_found = True
            if not self._part1_found:
                return IntroductorySectionElement.create_from_element(
                    element,
                    log_origin=self.__class__.__name__,
                )
        if context.iteration == 1:
            return element
        msg = "Unexpected iteration number"
        raise ValueError(msg)
