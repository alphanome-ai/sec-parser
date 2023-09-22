from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.exceptions.core_exceptions import (
    SecParserValueError,
)
from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


@dataclass
class ElementwiseParsingContext:
    """
    ElementwiseParsingContext class for passing context information
    to elementwise parsing plugins.
    """

    # is_root tells the plugin whether the given semantic element has
    # an HTML tag which is at the root level of the HTML document.
    is_root_element: bool


class AbstractElementwiseParsingPlugin(AbstractParsingPlugin):
    """
    `AbstractElementwiseParsingPlugin` class applies transformations
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

    def _transform(
        self,
        elements: list[AbstractSemanticElement],
        *,
        _context: ElementwiseParsingContext | None = None,
    ) -> list[AbstractSemanticElement]:
        context = _context or ElementwiseParsingContext(
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
                child_context = ElementwiseParsingContext(
                    is_root_element=False,
                )
                element.inner_elements = self._transform(
                    element.inner_elements,
                    _context=child_context,
                )

            elements[i] = element

        return elements

    @abstractmethod
    def _transform_element(
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
