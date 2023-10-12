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


def test_nesting_of_leveled_elements():
    # Arrange
    mock_elements = [
        LeveledElement(html_tag("tag1", "text1"), level=1),
        LeveledElement(html_tag("tag2", "text2"), level=2),
        LeveledElement(html_tag("tag3", "text3"), level=2),
    ]

    def get_rules() -> list[AbstractNestingRule]:
        return [NestSameTypeDependingOnLevelRule()]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 1
    assert isinstance(tree.root_nodes[0].semantic_element, LeveledElement)
    assert tree.root_nodes[0].semantic_element.level == 1
    assert len(tree.root_nodes[0].children) == 2
    for child in tree.root_nodes[0].children:
        assert isinstance(child.semantic_element, LeveledElement)
        assert child.semantic_element.level == 2


def test_always_nest_as_parent():
    # Arrange
    mock_elements = [
        ChildElement(html_tag("tag7", "text7")),
        ParentElement(html_tag("tag6", "text6")),
        ChildElement(html_tag("tag8", "text8")),
        ParentElement(html_tag("tag17", "text17")),
        ChildElement(html_tag("tag18", "text18")),
    ]

    def get_rules() -> list[AbstractNestingRule]:
        return [AlwaysNestAsParentRule(ParentElement)]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 3
    assert isinstance(tree.root_nodes[0].semantic_element, ChildElement)
    assert isinstance(tree.root_nodes[1].semantic_element, ParentElement)
    assert isinstance(tree.root_nodes[2].semantic_element, ParentElement)
    assert len(tree.root_nodes[1].children) == 1
    assert isinstance(tree.root_nodes[1].children[0].semantic_element, ChildElement)
    assert len(tree.root_nodes[2].children) == 1
    assert isinstance(tree.root_nodes[1].children[0].semantic_element, ChildElement)


def test_always_nest_as_child():
    # Arrange
    mock_elements = [
        ChildElement(html_tag("tag7", "text7")),
        ParentElement(html_tag("tag6", "text6")),
        ChildElement(html_tag("tag8", "text8")),
        ParentElement(html_tag("tag17", "text17")),
        ChildElement(html_tag("tag18", "text18")),
    ]

    def get_rules() -> list[AbstractNestingRule]:
        return [AlwaysNestAsChildRule(ChildElement)]

    tree_builder = TreeBuilder(get_rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 3
    assert isinstance(tree.root_nodes[0].semantic_element, ChildElement)
    assert isinstance(tree.root_nodes[1].semantic_element, ParentElement)
    assert isinstance(tree.root_nodes[2].semantic_element, ParentElement)
    assert len(tree.root_nodes[1].children) == 1
    assert isinstance(tree.root_nodes[1].children[0].semantic_element, ChildElement)
    assert len(tree.root_nodes[2].children) == 1
    assert isinstance(tree.root_nodes[1].children[0].semantic_element, ChildElement)


def test_smoke_test():
    # Arrange
    tag = bs4.Tag(name="p")
    tag.string = "Hello, world!"
    element = BaseElement(HtmlTag(tag))
    expected_tree = SemanticTree([TreeNode(element)])
    tree_builder = TreeBuilder()

    # Act
    actual_tree = tree_builder.build([element])

    # Assert
    assert actual_tree.render() == expected_tree.render()


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
