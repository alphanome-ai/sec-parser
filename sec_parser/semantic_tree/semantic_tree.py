from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    from sec_parser.semantic_tree.tree_node import TreeNode


class SemanticTree:
    def __init__(self, root_nodes: list[TreeNode]) -> None:
        self._root_nodes = root_nodes

    def __iter__(self) -> Iterator[TreeNode]:
        """Iterate over the root nodes of the tree."""
        yield from self._root_nodes

    @property
    def nodes(self) -> Iterator[TreeNode]:
        """
        Get all nodes in the semantic tree. This includes the root nodes and all
        their descendants.
        """
        for node in self._root_nodes:
            yield node
            yield from node.get_descendants()
