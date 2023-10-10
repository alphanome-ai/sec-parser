from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.exceptions.core_exceptions import SecParserValueError
from sec_parser.processing_steps.abstract_processing_step import AbstractTransformStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


@dataclass
class ElementwiseProcessingContext:
    """
    ElementwiseProcessingContext class for passing context information
    to elementwise processing steps.
    """

    # The is_root variable informs the processing step whether the given
    # semantic element has an HTML tag that is at the root level of the
    # HTML document.
    is_root_element: bool


class AbstractElementwiseTransformStep(AbstractTransformStep):
    """
    `AbstractElementwiseTransformStep` class applies transformations
    to a list of semantic and container elements. Transformations are
    applied recursively, element by element. The class can also be
    used to iterate over all elements without applying transformations.
    """

    def __init__(
        self,
        *,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__()
        self._processed_types = process_only or set()
        self._then_excluded_types = except_dont_process or set()
        if self._processed_types & self._then_excluded_types:
            msg = "Processed types and ignored types should not overlap."
            raise SecParserValueError(msg)

    def _process(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementwiseProcessingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        context = _context or ElementwiseProcessingContext(
            is_root_element=True,
        )

        for i, input_element in enumerate(elements):
            if self._processed_types and not any(
                isinstance(input_element, t) for t in self._processed_types
            ):
                continue
            if any(isinstance(input_element, t) for t in self._then_excluded_types):
                continue

            element = self._transform_element(input_element, context)

            if element.inner_elements:
                child_context = ElementwiseProcessingContext(
                    is_root_element=False,
                )
                element.inner_elements = self._process(
                    element.inner_elements,
                    _context=child_context,
                )

            elements[i] = element

        return elements

    @abstractmethod
    def _transform_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        """
        `transform_element` method is responsible for transforming a
        single semantic element into another.

        It can also be utilized to simply iterate over all
        elements without applying any transformations.
        """
        raise NotImplementedError
