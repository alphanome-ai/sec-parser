from abc import ABC, abstractmethod

from sec_parser.semantic_elements.abstract_semantic_elements import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    RootSectionElement,
    TitleElement,
)
from sec_parser.utils.base_factory import BaseFactory


class AbstractRule(ABC):
    @abstractmethod
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        pass


class RootSectionRule(AbstractRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        is_parent_root_section = isinstance(parent, RootSectionElement)
        is_child_root_section = isinstance(child, RootSectionElement)

        return is_parent_root_section and not is_child_root_section


class TitleLevelRule(AbstractRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        is_parent_root = isinstance(parent, RootSectionElement)
        is_child_root = isinstance(child, RootSectionElement)
        if is_parent_root or is_child_root:
            return False

        if isinstance(parent, TitleElement) and isinstance(child, TitleElement):
            return parent.level < child.level

        # If this point is reached, it's implied that the child is not a TitleElement.
        return isinstance(parent, TitleElement)


class RuleFactory(BaseFactory[AbstractRule]):
    pass
