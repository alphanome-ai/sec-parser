from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sec_parser.semantic_elements.base_semantic_element import (
        BaseSemanticElement,
    )


class AbstractSemanticElementParser(ABC):
    @abstractmethod
    def __init__(
        self,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def parse(self, html: str) -> list[BaseSemanticElement]:
        raise NotImplementedError
