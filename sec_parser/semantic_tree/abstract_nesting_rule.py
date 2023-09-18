from abc import ABC, abstractmethod

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class AbstractNestingRule(ABC):
    @abstractmethod
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        pass
