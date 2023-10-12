from unittest.mock import Mock

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)


class MockCompositeElement(CompositeSemanticElement):
    pass


class MockElement(AbstractSemanticElement):
    pass


def test_unwrap_elements_normal_with_include_containers():
    # Arrange
    elem1 = MockElement(Mock())
    elem2 = MockElement(Mock())
    composite = MockCompositeElement(Mock(), [elem1, elem2])
    elements: list[AbstractSemanticElement] = [composite]

    # Act
    result = CompositeSemanticElement.unwrap_elements(elements, include_containers=True)

    # Assert
    assert result == [composite, elem1, elem2]


def test_unwrap_elements_normal_without_include_containers():
    # Arrange
    elem1 = MockElement(Mock())
    elem2 = MockElement(Mock())
    composite = MockCompositeElement(Mock(), [elem1, elem2])
    elements: list[AbstractSemanticElement] = [composite]

    # Act
    result = CompositeSemanticElement.unwrap_elements(elements)

    # Assert
    assert result == [elem1, elem2]


# Test for empty list
def test_unwrap_elements_empty_list():
    # Arrange
    elements = []

    # Act
    result = CompositeSemanticElement.unwrap_elements(elements)

    # Assert
    assert result == []


# Test for list with no CompositeSemanticElement
def test_unwrap_elements_no_composite():
    # Arrange
    elem1 = MockElement(Mock())
    elem2 = MockElement(Mock())
    elements: list[AbstractSemanticElement] = [elem1, elem2]

    # Act
    result = CompositeSemanticElement.unwrap_elements(elements)

    # Assert
    assert result == [elem1, elem2]


# Test for nested CompositeSemanticElement
def test_unwrap_elements_nested_composite():
    # Arrange
    elem1 = MockElement(Mock())
    elem2 = MockElement(Mock())
    composite_inner = MockCompositeElement(Mock(), [elem1, elem2])
    composite_outer = MockCompositeElement(Mock(), [composite_inner])
    elements: list[AbstractSemanticElement] = [composite_outer]

    # Act
    result = MockCompositeElement.unwrap_elements(elements, include_containers=True)

    # Assert
    assert result == [composite_outer, composite_inner, elem1, elem2]
