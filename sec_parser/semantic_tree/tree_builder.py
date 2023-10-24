from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from sec_parser.semantic_elements.title_element import TitleElement
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from sec_parser.semantic_tree.nesting_rules import (
    AbstractNestingRule,
    AlwaysNestAsParentRule,
    NestSameTypeDependingOnLevelRule,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TreeBuilder:
    """
    Builds a semantic tree from a list of semantic elements.

    Why Use a Tree Structure?
    =========================
    Using a tree data structure allows for easier and more robust filtering of sections.
    With a tree, you can select specific branches to filter, making it straightforward
    to identify section boundaries. This approach is more maintainable and robust
    compared to attempting the same operations on a flat list of elements.

    Overview:
    =========
    1. Takes a list of semantic elements.
    2. Applies nesting rules to these elements.

    Customization:
    ==============
    The nesting process is customizable through a list of rules. These rules determine
    how new elements should be nested under existing ones.

    Advanced Customization:
    =======================
    You can supply your own set of rules by providing a callable to `get_rules`, which
    should return a list of `AbstractNestingRule` instances.
    """

    def __init__(
        self,
        get_rules: Callable[[], list[AbstractNestingRule]] | None = None,
    ) -> None:
        self.get_rules = get_rules or self.get_default_rules

    @staticmethod
    def get_default_rules() -> list[AbstractNestingRule]:
        return [
            AlwaysNestAsParentRule(TopLevelSectionTitle),
            # Both RootSectionRule and TitleRule nest all elements under them,
            # leading to a conflict where a decision between TopLevelSectionStartMarker
            # and TitleRule is needed. This conflict is resolved by excluding
            # TopLevelSectionStartMarker from the rule for TitleElements.
            AlwaysNestAsParentRule(
                TitleElement,
                exclude_children={TopLevelSectionTitle},
            ),
            NestSameTypeDependingOnLevelRule(),
        ]

    def build(self, elements: list[AbstractSemanticElement]) -> SemanticTree:
        rules = self.get_rules()

        # The 'stack' is a list used to remember the nodes (sections or elements)
        # we're currently looking at as we go through the document.
        # We use this stack to determine where new nodes should be placed.
        # If a node should be nested (like a subsection inside a section),
        # we find that 'parent' in the stack.
        # When a node is done (it has no more 'children'), it's removed from the stack.
        stack: list[TreeNode] = []

        root_nodes: list[TreeNode] = []

        for element in elements:
            new_node = TreeNode(element)
            parent_node = self._find_parent_node(new_node, stack, rules)

            if parent_node is not None:
                parent_node.add_child(new_node)
                stack.append(new_node)
            else:
                root_nodes.append(new_node)
                stack.append(new_node)

        return SemanticTree(root_nodes)

    def _find_parent_node(
        self,
        new_node: TreeNode,
        stack: list[TreeNode],
        rules: list[AbstractNestingRule],
    ) -> TreeNode | None:
        while stack:
            potential_parent = stack[-1]

            if self._should_nest_under(new_node, potential_parent, rules):
                return potential_parent

            stack.pop()
        return None

    def _should_nest_under(
        self,
        child_node: TreeNode,
        parent_node: TreeNode,
        rules: list[AbstractNestingRule],
    ) -> bool:
        results = tuple(
            rule.should_be_nested_under(
                child=child_node.semantic_element,
                parent=parent_node.semantic_element,
            )
            for rule in rules
        )
        return any(results)
