from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.semantic_tree_transformations.rules import (
    AbstractRule,
    RootSectionRule,
    RuleFactory,
    TitleLevelRule,
)
from sec_parser.semantic_tree_transformations.semantic_tree import SemanticTree
from sec_parser.semantic_tree_transformations.tree_node import TreeNode

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class TreeBuilder:
    @staticmethod
    def get_default_rules() -> list[type[AbstractRule] | RuleFactory]:
        return [RootSectionRule, TitleLevelRule]

    def __init__(
        self,
        rules: list[type[AbstractRule] | RuleFactory] | None = None,
    ) -> None:
        rules = rules or self.get_default_rules()
        self._rule_factories = [
            factory if isinstance(factory, RuleFactory) else RuleFactory(factory)
            for factory in rules
        ]

    def build(self, elements: list[AbstractSemanticElement]) -> SemanticTree:
        rules = [factory.create() for factory in self._rule_factories]
        stack: list[TreeNode] = []
        root_elements: list[TreeNode] = []

        for element in elements:
            parent_found = False
            new_node = TreeNode(element)

            while stack:
                potential_parent = stack[-1]

                if any(
                    rule.should_be_nested_under(
                        child=new_node.semantic_element,
                        parent=potential_parent.semantic_element,
                    )
                    for rule in rules
                ):
                    potential_parent.add_child(new_node)
                    parent_found = True
                    break

                stack.pop()

            if not parent_found:
                root_elements.append(new_node)
                stack.append(new_node)
            else:
                stack.append(new_node)

        return SemanticTree(root_elements)
