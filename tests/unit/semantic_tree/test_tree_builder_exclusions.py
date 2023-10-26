import bs4

from sec_parser import AbstractSemanticElement, TreeBuilder
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import \
    AbstractLevelElement
from sec_parser.semantic_tree.nesting_rules import AlwaysNestAsChildRule


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
    assert len(list(tree)) == 3
    assert isinstance(list(tree)[0].semantic_element, IgnoredParent)
    assert isinstance(list(tree)[1].semantic_element, ChildElement)
    assert isinstance(list(tree)[2].semantic_element, ParentElement)


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
    assert len(list(tree)) == 3
    assert isinstance(list(tree)[0].semantic_element, ParentElement)
    assert isinstance(list(tree)[1].semantic_element, IgnoredChild)
    assert isinstance(list(tree)[2].semantic_element, ParentElement)


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
    assert len(list(tree)) == 5
    assert isinstance(list(tree)[0].semantic_element, ParentElement)
    assert isinstance(list(tree)[1].semantic_element, ParentElement)
    assert isinstance(list(tree)[2].semantic_element, IgnoredChild)
    assert isinstance(list(tree)[3].semantic_element, IgnoredParent)
    assert isinstance(list(tree)[4].semantic_element, ChildElement)
