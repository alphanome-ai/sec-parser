from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.exceptions import SecParserError
from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import ErrorWhileProcessingElement

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


@dataclass
class ElementwiseProcessingContext:
    """
    The ElementwiseProcessingContext class is designed to provide context information
    for elementwise processing steps. This includes specifying whether an element is a
    root and tracking the current iteration in a series of repeated processing steps
    over all elements.

    Attributes
    ----------
        is_root_element (bool): Indicates if the given semantic element is a root
                                element in the HTML document.

        iteration (int): Represents the current iteration number during the repeated
                         processing of all semantic elements. This is related to the
                         `_NUM_ITERATIONS` constant in subclasses, which specifies
                         the total number of iterations that will be performed over
                         all elements.
    """

    is_root_element: bool
    iteration: int


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

    def _process(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementwiseProcessingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        for iteration in range(self._NUM_ITERATIONS):
            context = _context or ElementwiseProcessingContext(
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
                        child_context = ElementwiseProcessingContext(
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
                    elements[i] = ErrorWhileProcessingElement.create_from_element(
                        element,
                        error=e,
                        log_origin=self.__class__.__name__,
                    )

        return elements

    @abstractmethod
    def _process_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        """
        `_process_element` method is responsible for transforming a
        single semantic element into another.

        It can also be utilized to simply iterate over all
        elements without applying any transformations.
        """
        raise NotImplementedError  # pragma: no cover
