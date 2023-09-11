from abc import ABC, abstractmethod

from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)


class AbstractParsingPlugin(ABC):
    @abstractmethod
    def apply(self, root_tags: list[AbstractSemanticElement]) -> bool:
        raise NotImplementedError
