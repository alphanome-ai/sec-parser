from __future__ import annotations

from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_tree.tree_node import TreeNode


@pytest.fixture
def mock_element():
    return Mock(spec=AbstractSemanticElement)


def test_add_child(mock_element):
    # Arrange
    parent = TreeNode(mock_element)
    child = TreeNode(mock_element)

    # Act
    parent.add_child(child)

    # Assert
    assert parent.has_child(child)
    assert child.parent == parent


def test_add_children(mock_element):
    # Arrange
    parent = TreeNode(mock_element)
    children = [TreeNode(mock_element) for _ in range(3)]

    # Act
    parent.add_children(children)

    # Assert
    for child in children:
        assert parent.has_child(child)
        assert child.parent == parent


def test_remove_child(mock_element):
    # Arrange
    parent = TreeNode(mock_element)
    child = TreeNode(mock_element, parent=parent)

    # Act
    parent.remove_child(child)

    # Assert
    assert not parent.has_child(child)
    assert child.parent is None


def test_set_parent(mock_element):
    # Arrange
    node = TreeNode(mock_element)
    new_parent = TreeNode(mock_element)

    # Act
    node.parent = new_parent

    # Assert
    assert node.parent == new_parent
    assert new_parent.has_child(node)


def test_remove_from_existing_parent_when_new_parent_assigned(mock_element):
    # Arrange
    initial_parent = TreeNode(mock_element)
    node = TreeNode(mock_element, parent=initial_parent)
    new_parent = TreeNode(mock_element)

    # Act
    node.parent = new_parent

    # Assert
    assert node.parent == new_parent
    assert new_parent.has_child(node)
    assert not initial_parent.has_child(node)


def test_remove_parent(mock_element):
    # Arrange
    parent = TreeNode(mock_element)
    child = TreeNode(mock_element, parent=parent)

    # Act
    child.parent = None

    # Assert
    assert child.parent is None
    assert not parent.has_child(child)


def test_repr(mock_element):
    # Arrange
    parent = TreeNode(mock_element)
    children = [TreeNode(mock_element) for _ in range(3)]
    node_with_children = TreeNode(mock_element, children=children)

    # Act
    repr_parent = repr(parent)
    repr_with_children = repr(node_with_children)

    # Assert
    assert repr_parent == "TreeNode(parent=None, children=0)"
    assert repr_with_children == f"TreeNode(parent=None, children={len(children)})"
    repr_parent = repr(parent)
    repr_with_children = repr(node_with_children)

    # Assert
    assert repr_parent == "TreeNode(parent=None, children=0)"
    assert repr_with_children == f"TreeNode(parent=None, children={len(children)})"


@pytest.mark.parametrize(
    "tree_structure,expected_nodes",
    [
        # Test with an empty tree
        ({"root": []}, []),
        # Test with a single child node with no grandchildren
        ({"root": [{"child": []}]}, ["child"]),
        # Test with multiple child nodes with no grandchildren
        ({"root": [{"child1": []}, {"child2": []}]}, ["child1", "child2"]),
        # Test with a single child node with grandchildren
        (
            {"root": [{"child1": ["grandchild1", "grandchild2"]}]},
            ["child1", "grandchild1", "grandchild2"],
        ),
        # Test with multiple child nodes with grandchildren
        (
            {
                "superroot": [
                    {"root1": ["child1", {"child2": ["grandchild1", "grandchild2"]}]},
                    {"root2": ["child3"]},
                ],
            },
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
def test_get_descendants(
    tree_structure: dict | list[dict],
    expected_nodes: list[str],
) -> None:
    def build_tree(tree_structure, parent=None):
        nodes = []
        if not isinstance(tree_structure, list):
            tree_structure = [tree_structure]
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

    node = build_tree(tree_structure)[0]

    actual_nodes = list(node.get_descendants())

    assert [k.text for k in actual_nodes] == expected_nodes


class MockSemanticElement(AbstractSemanticElement):
    pass


def element(text):
    t = bs4.Tag(name="p")
    t.string = text
    return MockSemanticElement(HtmlTag(t))


# Test data table
test_data = [
    {"pretty": False, "expected_result": "<html>sample</html>"},
    {"pretty": True, "expected_result": "<html>\n  sample\n</html>"},
]


@pytest.mark.parametrize("test_case", test_data)
def test_tree_node_get_source_code(test_case):
    # Arrange
    pretty = test_case["pretty"]
    expected_result = test_case["expected_result"]
    mock_semantic_element = Mock()
    mock_semantic_element.get_source_code.return_value = expected_result
    tree_node = TreeNode(semantic_element=mock_semantic_element)

    # Act
    result = tree_node.get_source_code(pretty=pretty)

    # Assert
    assert result == expected_result
    mock_semantic_element.get_source_code.assert_called_once_with(pretty=pretty)
