from unittest.mock import Mock

import pytest

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
