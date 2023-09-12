from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class AbstractParsingPlugin(ABC):
    @abstractmethod
    def apply(
        self, elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement] | None:
        raise NotImplementedError
