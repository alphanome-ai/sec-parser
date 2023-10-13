from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from sec_parser.exceptions import SecParserRuntimeError
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

ElementTransformer = Callable[[AbstractSemanticElement], AbstractSemanticElement]


class AlreadyProcessedError(SecParserRuntimeError):
    pass


class AbstractProcessingStep(ABC):
    """
    AbstractProcessingStep class for transforming a list of elements.
    Chaining multiple steps together allows for complex transformations
    while keeping the code modular.

    Each instance of a step is designed to be used for a single
    transformation operation. This ensures that any internal state
    maintained during a transformation is isolated to the processing
    of a single document.
    """

    def __init__(self) -> None:
        """
        Initialize the step. Sets `_transformed` to False to ensure
        that each instance is used for exactly one transformation operation.
        """
        self._already_processed = False

    def process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        Transform the list of semantic elements.

        Note: The `elements` argument could potentially be mutated for
        performance reasons.
        """
        if self._already_processed:
            msg = (
                "This Step instance has already processed a document. "
                "Each Step instance is designed for a single "
                "transformation operation. Please create a new instance "
                "of the Step to process another document."
            )
            raise AlreadyProcessedError(msg)

        self._already_processed = True
        return self._process(elements)

    @abstractmethod
    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        Implement the actual transformation logic in child classes.

        This method is intended to be overridden by child classes to provide specific
        transformation logic.
        """
        raise NotImplementedError  # pragma: no cover
