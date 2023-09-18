from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


class AbstractParsingPlugin(ABC):
    """
    AbstractParsingPlugin class for transforming a list of elements.
    Chaining multiple plugins together allows for complex transformations
    while keeping the code modular.
    """

    @abstractmethod
    def transform(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        Transform the list of semantic elements.

        Note that the `elements` argument could potentially be mutated due
        to performance reasons.
        """
        raise NotImplementedError


@dataclass
class ElementwiseParsingContext:
    """
    ElementwiseParsingContext class for passing context information
    to elementwise parsing plugins.
    """

    # is_root tells the plugin whether the given semantic element has
    # an HTML tag which is at the root level of the HTML document.
    is_root: bool


class AbstractElementwiseParsingPlugin(AbstractParsingPlugin):
    """
    `AbstractElementwiseParsingPlugin` class applies transformations
    to a list of semantic and container elements. Transformations are
    applied recursively, element by element. The class can also be
    used to iterate over all elements without applying transformations.
    """

    def transform(
        self,
        elements: list[AbstractSemanticElement],
        _context: ElementwiseParsingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        context = _context or ElementwiseParsingContext(is_root=True)
        for i in range(len(elements)):
            element = self.transform_element(elements[i], context)
            if element.inner_elements:
                child_context = ElementwiseParsingContext(is_root=False)
                element.inner_elements = self.transform(
                    element.inner_elements,
                    child_context,
                )
            elements[i] = element
        return elements

    @abstractmethod
    def transform_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        """
        `transform_element` method is responsible for transforming a
        single semantic element into another.

        It can also be utilized to simply iterate over all
        elements without applying any transformations.
        """
        raise NotImplementedError
