from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TreeNode:
    def __init__(
        self: TreeNode,
        semantic_element: AbstractSemanticElement,
        *,
        parent: TreeNode | None = None,
        children: Iterable[TreeNode] | None = None,
    ) -> None:
        self.semantic_element = semantic_element
        self._parent = None
        self._children: list[TreeNode] = []
        self.parent = parent
        if children is not None:
            self.add_children(list(children))

    @property
    def children(self: TreeNode) -> list[TreeNode]:
        return self._children.copy()

    @property
    def parent(self: TreeNode) -> TreeNode | None:
        return self._parent

    @parent.setter
    def parent(self: TreeNode, parent: TreeNode | None) -> None:
        if self._parent is not None:
            self._parent.remove_child(self)
        if parent is not None:
            parent.add_child(self)
        self._parent = parent

    def add_child(self: TreeNode, child: TreeNode) -> None:
        if child not in self._children:
            self._children.append(child)
            if child.parent != self:
                child.parent = self

    def add_children(self: TreeNode, children: Iterable[TreeNode]) -> None:
        for child in children:
            self.add_child(child)

    def remove_child(self: TreeNode, child: TreeNode) -> None:
        if child in self._children:
            self._children.remove(child)
            if child.parent == self:
                child.parent = None

    def has_child(self: TreeNode, child: TreeNode) -> bool:
        return child in self._children

    def __repr__(self: TreeNode) -> str:
        return f"TreeNode(parent={self.parent}, children={len(self._children)})"
