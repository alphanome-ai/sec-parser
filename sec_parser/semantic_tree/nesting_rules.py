from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sec_parser.semantic_elements.semantic_elements import AbstractLevelElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class AbstractNestingRule(ABC):
    """
    AbstractNestingRule is a base class for defining rules for nesting
    semantic elements. Each rule should ideally mention at most one or
    two types of semantic elements to reduce coupling and complexity.

    In case of conflicts between rules, they should be resolved through
    parameters like exclude_parents and exclude_children.
    """

    def __init__(self,
                 *,
                 exclude_parents: set[type[AbstractSemanticElement]]|None = None,
                 exclude_children: set[type[AbstractSemanticElement]]|None = None,
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

class AlwaysNestAsParentRule(AbstractNestingRule):
    def __init__(
        self,
        cls: type[AbstractSemanticElement],
        /,
        *,
        exclude_parents: set[type[AbstractSemanticElement]] | None = None,
        exclude_children: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            exclude_parents=exclude_parents,
            exclude_children=exclude_children,
        )
        self._cls = cls

    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (isinstance(parent, self._cls)
            and not isinstance(child, self._cls))

class AlwaysNestAsChildRule(AbstractNestingRule):
    def __init__(
        self,
        cls: type[AbstractSemanticElement],
        /,
        *,
        exclude_parents: set[type[AbstractSemanticElement]] | None = None,
        exclude_children: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            exclude_parents=exclude_parents,
            exclude_children=exclude_children,
        )
        self._cls = cls

    def _should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return (not isinstance(parent, self._cls)
            and isinstance(child, self._cls))


class NestSameTypeDependingOnLevelRule(AbstractNestingRule):
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
