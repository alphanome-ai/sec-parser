from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.processing_steps.abstract_processing_step import AbstractProcessingStep
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


@dataclass
class ElementwiseProcessingContext:
    """
    ElementwiseProcessingContext class for passing context information
    to elementwise processing steps.
    """

    # The is_root variable informs the processing step whether the given
    # semantic element wraps an HTML tag that is at the top level of the
    # HTML document.
    is_root_element: bool


class AbstractElementwiseProcessingStep(AbstractProcessingStep):
    """
    `AbstractElementwiseTransformStep` class is used to iterate over
    all Semantic Elements with or without applying transformations.
    """

    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__()
        self._types_to_process = types_to_process or set()
        self._types_to_exclude = types_to_exclude or set()

    def _process(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementwiseProcessingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        context = _context or ElementwiseProcessingContext(
            is_root_element=True,
        )

        for i, e in enumerate(elements):
            # avoids lint error "`element` overwritten by assignment target"
            element = e

            if self._types_to_process and not any(
                isinstance(element, t) for t in self._types_to_process
            ):
                continue
            if any(isinstance(element, t) for t in self._types_to_exclude):
                continue

            if isinstance(element, CompositeSemanticElement):
                child_context = ElementwiseProcessingContext(
                    is_root_element=False,
                )
                element.inner_elements = self._process(
                    element.inner_elements,
                    _context=child_context,
                )
            else:
                element = self._process_element(element, context)

            elements[i] = element

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
