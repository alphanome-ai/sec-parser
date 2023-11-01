from __future__ import annotations

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode


class MockSemanticElement(AbstractSemanticElement):
    pass


def element(text):
    t = bs4.Tag(name="p")
    t.string = text
    return MockSemanticElement(HtmlTag(t))


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


@pytest.mark.parametrize(
    ("name", "tree_structure", "render_kwargs", "expected_output"),
    values := [
        ("empty_tree_with_default_kwargs", [], {}, ""),
    ],
    ids = [v[0] for v in values],
)
def test_render(name, tree_structure, render_kwargs, expected_output):
    # Arrange
    root_nodes = build_tree(tree_structure)
    tree = SemanticTree(root_nodes)
    
    # Act
    actual = tree.render(**render_kwargs)

    # Assert
    assert actual==expected_output


@pytest.mark.parametrize(
    ("name", "tree_structure", "print_kwargs", "expected_output"),
    values := [
        (
            "empty_tree_with_default_kwargs", 
            [], 
            {}, 
            "\n"
        ),
        (
            "simple_tree", 
            [{"root": ["child1", "child2"]}], 
            {}, 
            "\x1b[1;34mMockSemanticElement\x1b[0m: root\n├── \x1b[1;34mMockSemanticElement\x1b[0m: child1\n└── \x1b[1;34mMockSemanticElement\x1b[0m: child2\n"
        ),
        (
            "simple_tree_with_line_limit",
            [{"root": ["child1", "child2"]}], 
            {
                "line_limit": 2,
            },
            "\x1b[1;34mMockSemanticElement\x1b[0m: root\n├── \x1b[1;34mMockSemanticElement\x1b[0m: child1\n",
        ),
    ],
    ids = [v[0] for v in values],
)
def test_print(name, tree_structure, print_kwargs, expected_output, capsys):
    # Arrange
    root_nodes = build_tree(tree_structure)
    tree = SemanticTree(root_nodes)
    
    # Act
    tree.print(**print_kwargs)
    actual = capsys.readouterr().out

    # Assert
    assert actual==expected_output


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
    # Arrange
    root_nodes = build_tree(tree_structure)
    tree = SemanticTree(root_nodes)

    # Act
    nodes = list(tree.nodes)

    # Assert
    assert [node.text for node in nodes] == expected_nodes