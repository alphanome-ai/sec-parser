from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from sec_parser.exceptions.core_exceptions import (
    SecParserRuntimeError,
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

