from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractSingleElementCheck(ABC):
    @abstractmethod
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        """
        Designed to work as series of subsequent checks.
        - Returning None means that the check is inconclusive, and the next check should be performed.
        - Returning True means that no further checks are necessary, and the HTML element will be
        later be able to be converted into a semantic element without any splits.
        - Returning False means that the HTML element will be split into multiple semantic elements
        of type NotYetClassifiedElement.
        """
        raise NotImplementedError  # pragma: no cover
