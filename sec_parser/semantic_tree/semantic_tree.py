from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_tree.tree_node import TreeNode


class SemanticTree:
    def __init__(self, root_nodes: list[TreeNode]) -> None:
        self.root_nodes = root_nodes
