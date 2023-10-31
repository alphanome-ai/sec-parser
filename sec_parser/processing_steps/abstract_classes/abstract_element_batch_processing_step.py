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

if TYPE_CHECKING: # pragma: no cover
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

    def _process(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementProcessingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        for iteration in range(self._NUM_ITERATIONS):
            context = _context or ElementProcessingContext(
                is_root_element=True,
                iteration=iteration,
            )

            for element in elements:
                if isinstance(element, CompositeSemanticElement):
                    child_context = ElementProcessingContext(
                        is_root_element=False,
                        iteration=iteration,
                    )
                    element.inner_elements = tuple(
                        self._process(
                            list(element.inner_elements),
                            _context=child_context,
                        ),
                    )
            elements = self._process_elements(elements, context)

        return elements
