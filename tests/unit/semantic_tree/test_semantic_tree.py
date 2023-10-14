from __future__ import annotations

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode


@pytest.mark.parametrize(
    "tree_structure,expected_nodes",
    [
        # Test with an empty tree
        ([], []),
        # Test with a single root node with no children
        ([{"root": []}], ["root"]),
        # Test with multiple root nodes with no children
        ([{"root1": []}, {"root2": []}], ["root1", "root2"]),
        # Test with a single root node with children
        ([{"root": ["child1", "child2"]}], ["root", "child1", "child2"]),
        # Test with multiple root nodes with children
        (
            [
                {"root1": ["child1", {"child2": ["grandchild1", "grandchild2"]}]},
                {"root2": ["child3"]},
            ],
            [
                "root1",
                "child1",
                "child2",
                "grandchild1",
                "grandchild2",
                "root2",
                "child3",
            ],
        ),
    ],
)
def test_get_nodes(
    tree_structure: dict | list[dict],
    expected_nodes: list[str],
) -> None:
    def build_tree(tree_structure, parent=None):
        nodes = []
        assert isinstance(tree_structure, list)
        for item in tree_structure:
            if isinstance(item, dict):
                for key, value in item.items():
                    # Create a new TreeNode for each key
                    node = TreeNode(element(key), parent=parent)
                    nodes.append(node)
                    # Recursively build the tree for the children of the node
                    if isinstance(value, list):
                        children = build_tree(value, parent=node)
                        node.add_children(children)
            else:
                child_node = TreeNode(element(item), parent=parent)
                nodes.append(child_node)
        return nodes

    root_nodes = build_tree(tree_structure)
    tree = SemanticTree(root_nodes)

    # Act
    nodes = list(tree.nodes)

    # Assert
    assert [node.text for node in nodes] == expected_nodes


class MockSemanticElement(AbstractSemanticElement):
    pass


def element(text):
    t = bs4.Tag(name="p")
    t.string = text
    return MockSemanticElement(HtmlTag(t))
