import bs4

from sec_parser import AbstractSemanticElement, TreeBuilder
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import AbstractLevelElement
from sec_parser.semantic_tree.nesting_rules import (
    AbstractNestingRule,
    AlwaysNestAsChildRule,
    AlwaysNestAsParentRule,
    NestSameTypeDependingOnLevelRule,
)
from sec_parser.semantic_tree.semantic_tree import SemanticTree
from sec_parser.semantic_tree.tree_node import TreeNode


def html_tag(tag_name: str, text: str) -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


class BaseElement(AbstractSemanticElement):
    pass


class ParentElement(AbstractSemanticElement):
    pass


class ChildElement(AbstractSemanticElement):
    pass


class IgnoredParent(AbstractSemanticElement):
    pass


class IgnoredChild(AbstractSemanticElement):
    pass


class LeveledElement(AbstractLevelElement):
    pass


def test_exclude_ignored_parent():
    # Arrange
    mock_elements = [
        IgnoredParent(html_tag("tag2", "text2")),
        ChildElement(html_tag("tag1", "text1")),
        ParentElement(html_tag("tag3", "text3")),
        ChildElement(html_tag("tag1", "text1")),
    ]

    def get_rules():
        return [AlwaysNestAsChildRule(ChildElement, exclude_parents={IgnoredParent})]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 3
    assert isinstance(tree.root_nodes[0].semantic_element, IgnoredParent)
    assert isinstance(tree.root_nodes[1].semantic_element, ChildElement)
    assert isinstance(tree.root_nodes[2].semantic_element, ParentElement)


def test_exclude_ignored_child():
    # Arrange
    mock_elements = [
        ParentElement(html_tag("tag2", "text2")),
        IgnoredChild(html_tag("tag1", "text1")),
        ParentElement(html_tag("tag3", "text3")),
        ChildElement(html_tag("tag1", "text1")),
    ]

    def get_rules():
        return [AlwaysNestAsChildRule(ChildElement, exclude_children={IgnoredChild})]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 3
    assert isinstance(tree.root_nodes[0].semantic_element, ParentElement)
    assert isinstance(tree.root_nodes[1].semantic_element, IgnoredChild)
    assert isinstance(tree.root_nodes[2].semantic_element, ParentElement)


def test_exclude_both_ignored_parent_and_child():
    # Arrange
    mock_elements = [
        ParentElement(html_tag("tag2", "text2")),
        ChildElement(html_tag("tag1", "text1")),
        ParentElement(html_tag("tag3", "text3")),
        IgnoredChild(html_tag("tag1", "text1")),
        IgnoredParent(html_tag("tag2", "text2")),
        ChildElement(html_tag("tag1", "text1")),
    ]

    def get_rules():
        return [
            AlwaysNestAsChildRule(
                ChildElement,
                exclude_parents={IgnoredParent},
                exclude_children={IgnoredChild},
            ),
        ]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 5
    assert isinstance(tree.root_nodes[0].semantic_element, ParentElement)
    assert isinstance(tree.root_nodes[1].semantic_element, ParentElement)
    assert isinstance(tree.root_nodes[2].semantic_element, IgnoredChild)
    assert isinstance(tree.root_nodes[3].semantic_element, IgnoredParent)
    assert isinstance(tree.root_nodes[4].semantic_element, ChildElement)
