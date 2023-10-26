import bs4

from sec_parser import AbstractSemanticElement, TreeBuilder
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import AbstractLevelElement
from sec_parser.semantic_tree.nesting_rules import (
    AbstractNestingRule,
    NestSameTypeDependingOnLevelRule,
)


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
    assert len(list(tree)) == 1
    assert isinstance(list(tree)[0].semantic_element, LeveledElement)
    assert list(tree)[0].semantic_element.level == 1
    assert len(list(tree)[0].children) == 2
    for child in list(tree)[0].children:
        assert isinstance(child.semantic_element, LeveledElement)
        assert child.semantic_element.level == 2
