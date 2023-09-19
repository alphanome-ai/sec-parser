from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from sec_parser.exceptions.core_exceptions import (
    SecParserRuntimeError,
    SecParserValueError,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


class AlreadyTransformedError(SecParserRuntimeError):
    pass


class AbstractParsingPlugin(ABC):
    """
    AbstractParsingPlugin class for transforming a list of elements.
    Chaining multiple plugins together allows for complex transformations
    while keeping the code modular.

    Each instance of a plugin is designed to be used for a single
    transformation operation. This ensures that any internal state
    maintained during a transformation is isolated to the processing
    of a single document.
    """

    def __init__(self) -> None:
        """
        Initialize the plugin. Sets `_transformed` to False to ensure
        that each instance is used for exactly one transformation operation.
        """
        self._transformed = False

    def transform(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        Transform the list of semantic elements.

        Note: The `elements` argument could potentially be mutated for
        performance reasons.
        """
        if self._transformed:
            msg = (
                "This Plugin instance has already processed a document. "
                "Each plugin instance is designed for a single "
                "transformation operation. Please create a new instance "
                "of the Plugin to process another document."
            )
            raise AlreadyTransformedError(msg)

        self._transformed = True
        return self._transform(elements)

    @abstractmethod
    def _transform(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        Implement the actual transformation logic in child classes.

        This method is intended to be overridden by child classes to provide specific
        transformation logic.
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
    is_root_element: bool

    # current_iteration keeps track of the current iteration over
    # all of the elements
    current_iteration: int = 0


class AbstractElementwiseParsingPlugin(AbstractParsingPlugin):
    """
    `AbstractElementwiseParsingPlugin` class applies transformations
    to a list of semantic and container elements. Transformations are
    applied recursively, element by element. The class can also be
    used to iterate over all elements without applying transformations.
    """

    # iteration_count specifies the number of times the plugin should iterate
    # over all the elements. This allows child classes to opt for multiple
    # passes over the elements for more complex transformations.
    iteration_count: int = 1

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
        context = _context or ElementwiseParsingContext(is_root_element=True)
        for current_iteration in range(self.iteration_count):
            context = _context or ElementwiseParsingContext(
                is_root_element=True,
                current_iteration=current_iteration,
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
                        current_iteration=current_iteration,
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
