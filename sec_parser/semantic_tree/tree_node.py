from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable, Iterator

    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TreeNode:
    """
    The TreeNode class is a fundamental part of the semantic tree structure.
    Each TreeNode represents a node in the tree. It holds a reference to a semantic
    element, maintains a list of its child nodes, and a reference to its parent node.
    This class provides methods for managing the tree structure, such as adding and
    removing child nodes.
    Importantly, these methods ensure logical consistency as children/parents are
    being changed.
    For example, if a parent is removed from a child, the child is automatically
    removed from the parent.
    """

    def __init__(
        self: TreeNode,
        semantic_element: AbstractSemanticElement,
        *,
        parent: TreeNode | None = None,
        children: Iterable[TreeNode] | None = None,
    ) -> None:
        self._semantic_element = semantic_element
        self._children: list[TreeNode] = []
        self._parent: TreeNode | None = None
        self.parent = parent  # call 'parent` setter
        if children is not None:
            self.add_children(list(children))

    @property
    def semantic_element(self) -> AbstractSemanticElement:
        return self._semantic_element

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

    def get_descendants(self: TreeNode) -> Iterator[TreeNode]:
        for child in self._children:
            yield child
            yield from child.get_descendants()

    def __repr__(self: TreeNode) -> str:
        return f"TreeNode(parent={self.parent}, children={len(self._children)})"

    @property
    def text(self) -> str:
        """Property text is a passthrough to the SemanticElement text property."""
        return self._semantic_element.text

    def get_source_code(self, *, pretty: bool = False) -> str:
        """get_source_code is a passthrough to the SemanticElement method."""
        return self._semantic_element.get_source_code(pretty=pretty)
