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
    assert len(list(tree)) == 3
    assert isinstance(list(tree)[0].semantic_element, ChildElement)
    assert isinstance(list(tree)[1].semantic_element, ParentElement)
    assert isinstance(list(tree)[2].semantic_element, ParentElement)
    assert len(list(tree)[1].children) == 1
    assert isinstance(list(tree)[1].children[0].semantic_element, ChildElement)
    assert len(list(tree)[2].children) == 1
    assert isinstance(list(tree)[1].children[0].semantic_element, ChildElement)
