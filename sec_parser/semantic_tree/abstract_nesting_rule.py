from abc import ABC, abstractmethod

from sec_parser.semantic_elements.base_semantic_element import (
    BaseSemanticElement,
)


class AbstractNestingRule(ABC):
    @abstractmethod
    def should_be_nested_under(
        self,
        parent: BaseSemanticElement,
        child: BaseSemanticElement,
    ) -> bool:
        pass
