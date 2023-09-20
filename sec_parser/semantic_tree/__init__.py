"""
The semantic_tree subpackage focuses on storing and
manipulating Semantic Elements in a tree data structure.
"""
from sec_parser.semantic_tree.abstract_nesting_rule import AbstractNestingRule
from sec_parser.semantic_tree.nesting_rules import (
    AlwaysNestAsChildRule,
    AlwaysNestAsParentRule,
    NestSameTypeDependingOnLevelRule,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_builder import TreeBuilder
from sec_parser.semantic_tree.tree_node import TreeNode

__all__ = [
    "AbstractNestingRule",
    "NestSameTypeDependingOnLevelRule",
    "SemanticTree",
    "TreeBuilder",
    "TreeNode",
    "AlwaysNestAsParentRule",
    "NestSameTypeDependingOnLevelRule",
    "AlwaysNestAsChildRule",
]
