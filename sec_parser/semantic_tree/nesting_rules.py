from abc import ABC, abstractmethod

from sec_parser.semantic_elements.base_semantic_element import (
    BaseSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    RootSectionElement,
    TitleElement,
)


class AbstractNestingRule(ABC):
    @abstractmethod
    def should_be_nested_under(
        self,
        parent: BaseSemanticElement,
        child: BaseSemanticElement,
    ) -> bool:
        pass


class RootSectionRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: BaseSemanticElement,
        child: BaseSemanticElement,
    ) -> bool:
        is_parent_root = isinstance(parent, RootSectionElement)
        is_child_not_root = not isinstance(child, RootSectionElement)
        return is_parent_root and is_child_not_root


class TitleLevelRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: BaseSemanticElement,
        child: BaseSemanticElement,
    ) -> bool:
        if isinstance(parent, RootSectionElement):
            return False

        if isinstance(parent, TitleElement):
            if isinstance(child, TitleElement):
                return parent.level < child.level
            return True

        return False
