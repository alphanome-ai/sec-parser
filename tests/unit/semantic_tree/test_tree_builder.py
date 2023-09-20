from sec_parser import (
    AbstractNestingRule,
    AbstractSemanticElement,
    HtmlTag,
    TreeBuilder,
)
from sec_parser.semantic_elements.abstract_semantic_element import AbstractLevelElement
from sec_parser.semantic_tree.nesting_rules import LevelsRule


class BaseElement(AbstractSemanticElement):
    pass


class ParentElement(AbstractSemanticElement):
    pass


class ChildElement(AbstractSemanticElement):
    pass


class LeveledElement(AbstractLevelElement):
    pass


class ParentChildNestingRule(AbstractNestingRule):
    def should_be_nested_under(
        self,
        parent: AbstractSemanticElement,
        child: AbstractSemanticElement,
    ) -> bool:
        return isinstance(parent, ParentElement) and isinstance(child, ChildElement)


def test_nesting_of_leveled_elements():
    # Arrange
    mock_elements = [
        # This is how elements are usually created in the parsing process:
        LeveledElement.convert_from(BaseElement(None, []), level=1),
        LeveledElement.convert_from(BaseElement(None, []), level=2),
        LeveledElement.convert_from(BaseElement(None, []), level=2),
    ]
    rules = [LevelsRule()]
    tree_builder = TreeBuilder(create_default_rules=lambda: rules)

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


def test_nesting_of_parent_and_child():
    # Arrange
    mock_elements = [
        # This is how elements are usually created in the parsing process:
        ParentElement.convert_from(BaseElement(None, [])),
        ChildElement.convert_from(BaseElement(None, [])),
    ]
    rules = [ParentChildNestingRule()]
    tree_builder = TreeBuilder(create_default_rules=lambda: rules)

    # Act
    tree = tree_builder.build(mock_elements)

    # Assert
    assert len(tree.root_nodes) == 1
    assert isinstance(tree.root_nodes[0].semantic_element, ParentElement)
    assert len(tree.root_nodes[0].children) == 1
    assert isinstance(tree.root_nodes[0].children[0].semantic_element, ChildElement)
