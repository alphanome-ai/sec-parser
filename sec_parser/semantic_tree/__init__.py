"""
The semantic_tree subpackage focuses on storing and
manipulating Semantic Elements in a tree data structure.
"""

from sec_parser.semantic_tree.rules import (
    AbstractNestingRule,
    RootSectionRule,
    TitleLevelRule,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_builder import TreeBuilder
from sec_parser.semantic_tree.tree_node import TreeNode

__all__ = [
    "AbstractNestingRule",
    "RootSectionRule",
    "TitleLevelRule",
    "SemanticTree",
    "TreeBuilder",
    "TreeNode",
]
