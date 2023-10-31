from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from loguru import logger

from sec_parser.exceptions import SecParserError
from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.processing_context import (
    ElementProcessingContext,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import ErrorWhileProcessingElement

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractElementwiseProcessingStep(AbstractProcessingStep):
    """
    `AbstractElementwiseTransformStep` class is used to iterate over
    all Semantic Elements with or without applying transformations.
    """

    # _NUM_ITERATIONS specifies the number of times this subclass will
    # iterate over all semantic elements. Modify this constant to \
    # change the iteration count.
    _NUM_ITERATIONS = 1

    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__()
        self._types_to_process = types_to_process or set()
        if types_to_process:
            self._types_to_process.add(CompositeSemanticElement)
        self._types_to_exclude = types_to_exclude or set()
        self._types_to_exclude.add(ErrorWhileProcessingElement)

    @abstractmethod
    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        """
        `_process_element` method is responsible for transforming a
        single semantic element into another.

        It can also be utilized to simply iterate over all
        elements without applying any transformations.
        """
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
            for i, e in enumerate(elements):
                # avoids lint error "`element` overwritten by assignment target"
                element = e

                try:
                    if self._types_to_process and not any(
                        isinstance(element, t) for t in self._types_to_process
                    ):
                        continue
                    if any(isinstance(element, t) for t in self._types_to_exclude):
                        continue

                    if isinstance(element, CompositeSemanticElement):
                        child_context = ElementProcessingContext(
                            is_root_element=False,
                            iteration=iteration,
                        )
                        inner_elements = self._process(
                            list(element.inner_elements),
                            _context=child_context,
                        )
                        element.inner_elements = tuple(inner_elements)
                    else:
                        element = self._process_element(element, context)

                    elements[i] = element
                except SecParserError as e:
                    logger.exception(e)
                    elements[i] = ErrorWhileProcessingElement.create_from_element(
                        element,
                        error=e,
                        log_origin=self.__class__.__name__,
                    )

        return elements
