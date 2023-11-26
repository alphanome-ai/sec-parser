from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.processing_context import (
    ElementProcessingContext,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractElementBatchProcessingStep(AbstractProcessingStep):
    _NUM_ITERATIONS = 1

    @abstractmethod
    def _process_elements(
        self,
        elements: list[AbstractSemanticElement],
        context: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        raise NotImplementedError  # pragma: no cover

    def _process_recursively(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        for element in elements:
            if isinstance(element, CompositeSemanticElement):
                element.inner_elements = tuple(
                    self._process_recursively(
                        list(element.inner_elements),
                        _context=_context,
                    ),
                )
        return self._process_elements(elements, _context)

    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        for iteration in range(self._NUM_ITERATIONS):
            context = ElementProcessingContext(
                iteration=iteration,
            )
            elements = self._process_recursively(elements, _context=context)

        return elements
