from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractSingleElementCheck(ABC):
    @abstractmethod
    def contains_single_element(self, element: AbstractSemanticElement) -> bool | None:
        raise NotImplementedError  # pragma: no cover
