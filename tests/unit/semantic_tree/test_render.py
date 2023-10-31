# test_semantic_tree.py

from typing import Callable

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import IrrelevantElement
from sec_parser.semantic_tree.render_ import render
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode


class Element(AbstractSemanticElement):
    pass


class ElementWithLevel(AbstractLevelElement):
    pass


class IgnoredElement(AbstractSemanticElement):
    pass


def test_tree_argument_overloading():
    # Arrange
    tree1 = new_node("p", "")
    tree2 = [tree1]
    tree3 = SemanticTree(tree2)
    tree4 = [new_element("p", "")]

    # Act
    result1 = render(tree1, pretty=False)
    result2 = render(tree2, pretty=False)
    result3 = render(tree3, pretty=False)
    result4 = render(tree4, pretty=False)

    # Assert
    assert result1.strip()
    assert result1 == result2 == result3 == result4


def test_tree_argument_overloading_exceptions():
    # Arrange
    unexpected_element = 42
    unexpected_tree = [unexpected_element]

    # Act & Assert
    with pytest.raises(TypeError):
        render(unexpected_element)
    
    with pytest.raises(TypeError):
        render(unexpected_tree)


def test_basic_render():
    # Arrange
    tree = get_tree()

    # Act
    result = render(list(tree), pretty=False)

    # Assert
    assert (
        result
        == "Element\n├── ElementWithLevel: Child 1 of node1\n├── Element: Child 2 of node1, with its own child\n│   └── Element: Grandchild of node1 (Child of node5)\n└── Element: Another child for node1\nElement: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )


def test_render_with_pretty_option():
    # Arrange
    tree = get_tree()

    # Act
    result = render(list(tree), pretty=True)

    # Assert
    assert (
        result
        == "\x1b[1;34mElement\x1b[0m\n├── \x1b[1;34mElementWithLevel\x1b[0m: Child 1 of node1\n├── \x1b[1;34mElement\x1b[0m: Child 2 of node1, with its own child\n│   └── \x1b[1;34mElement\x1b[0m: Grandchild of node1 (Child of node5)\n└── \x1b[1;34mElement\x1b[0m: Another child for node1\n\x1b[1;34mElement\x1b[0m: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )


def test_render_with_pretty_and_verbose_option():
    # Arrange
    tree = get_tree()

    # Act
    result = render(list(tree), pretty=True, verbose=True)

    # Assert
    assert (
        result
        == "\x1b[1;34mElement\x1b[0m\n├── \x1b[1;34mElementWithLevel\x1b[1;92m[L2]\x1b[0m\x1b[0m: Child 1 of node1\n├── \x1b[1;34mElement\x1b[0m: Child 2 of node1, with its own child\n│   └── \x1b[1;34mElement\x1b[0m: Grandchild of node1 (Child of node5)\n└── \x1b[1;34mElement\x1b[0m: Another child for node1\n\x1b[1;34mElement\x1b[0m: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )


def new_element(name, text):
    tag = bs4.Tag(name=name)
    tag.string = text
    return Element(HtmlTag(tag))


def new_node(name, text, cls: Callable = lambda k: Element(k)):
    tag = bs4.Tag(name=name)
    tag.string = text
    return TreeNode(cls(HtmlTag(tag)))


def get_tree():
    node1 = new_node("p", "")  # A regular node
    node2 = new_node("p", "A" * 70)  # A node with title longer than char_display_limit
    node3 = new_node(
        "p",
        "This is an ignored type",
        cls=lambda k: IrrelevantElement(k),
    )
    node4 = new_node(
        "p",
        "Child 1 of node1",
        cls=lambda k: ElementWithLevel(k, level=2),
    )
    node5 = new_node("p", "Child 2 of node1, with its own child")
    node6 = new_node("p", "Grandchild of node1 (Child of node5)")
    node7 = new_node("p", "Another child for node1")

    # Building the relationships
    node1.add_child(node4)
    node1.add_child(node5)
    node5.add_child(node6)
    node1.add_child(node7)

    tree = SemanticTree(
        [
            node1,
            node2,
            node3,
        ],
    )
    return tree
