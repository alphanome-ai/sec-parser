from abc import ABC, abstractmethod

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    AbstractLevelElement,
    BulletpointTextElement,
    RootSectionElement,
    TextElement,
)


class AbstractNestingRule(ABC):
    @abstractmethod
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        pass


class RootSectionRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        is_parent_root = isinstance(parent, RootSectionElement)
        is_child_not_root = not isinstance(child, RootSectionElement)
        return is_parent_root and is_child_not_root


class LevelsRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (
            parent.__class__ == child.__class__
            and isinstance(parent, AbstractLevelElement)
            and isinstance(child, AbstractLevelElement)
            and parent.level < child.level
        )


class BulletpointRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (
            isinstance(parent, TextElement)
            and not isinstance(parent, BulletpointTextElement)
            and isinstance(child, BulletpointTextElement)
        )
