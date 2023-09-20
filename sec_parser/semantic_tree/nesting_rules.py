from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sec_parser.semantic_elements.semantic_elements import (
    AbstractLevelElement,
    BulletpointTextElement,
    RootSectionElement,
    TextElement,
    TitleElement,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractNestingRule(ABC):
    def __init__(self,
                 *,
                 exclude_parents: set[type[AbstractNestingRule]]|None = None,
                 exclude_children: set[type[AbstractNestingRule]]|None = None,
                 ) -> None:
        super().__init__()
        self._exclude_parents = exclude_parents
        self._exclude_children = exclude_children

    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        if (self._exclude_parents
            and any(isinstance(parent, t) for t in self._exclude_parents)):
            return False
        if (self._exclude_children
            and any(isinstance(child, t) for t in self._exclude_children)):
            return False
        return self._should_be_nested_under(parent, child)

    @abstractmethod
    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        raise NotImplementedError


class RootSectionRule(AbstractNestingRule):
    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (isinstance(parent, RootSectionElement)
            and not isinstance(child, RootSectionElement))

class TitleRule(AbstractNestingRule):
    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (isinstance(parent, TitleElement)
            and not isinstance(child, TitleElement))

class LevelsRule(AbstractNestingRule):
    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (
            parent.__class__ == child.__class__
            and isinstance(parent, AbstractLevelElement)
            # this is logically implied, but keeping for clarity
            and isinstance(child, AbstractLevelElement)
            # level 1 is the top-most (root) level
            and parent.level < child.level
        )



class BulletpointRule(AbstractNestingRule):
    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (
            isinstance(parent, TextElement)
            and not isinstance(parent, BulletpointTextElement)
            and isinstance(child, BulletpointTextElement)
        )
