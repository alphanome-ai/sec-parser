from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement

MockHtmlTag = Mock()


@pytest.fixture
def default_inner_elements():
    return (NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p"))),)


@pytest.fixture
def inner_elements_with_composite():
    not_yet_classified = NotYetClassifiedElement(HtmlTag(bs4.Tag(name="p")))
    composite = CompositeSemanticElement(MockHtmlTag(), (), (not_yet_classified,))
    not_yet_classified.append_to_transformation_history(composite)
    return (not_yet_classified,)


def test_composite_semantic_element_initialization_valid_inner_elements(
    default_inner_elements,
):
    """Test if a CompositeSemanticElement object can be initialized with valid inner elements."""
    # Arrange
    mock_html_tag = MockHtmlTag()

    # Act
    element = CompositeSemanticElement(mock_html_tag, (), default_inner_elements)

    # Assert
    assert element.inner_elements == default_inner_elements
    assert element.html_tag == mock_html_tag


@pytest.mark.parametrize(
    "inner_elements, expected_exception, expected_message",
    [
        (None, ValueError, "inner_elements cannot be None or empty."),
        ((), ValueError, "inner_elements cannot be None or empty."),
    ],
)
def test_composite_semantic_element_initialization_with_invalid_inner_elements(
    inner_elements, expected_exception, expected_message
):
    """Test initialization with invalid inner_elements."""
    # Arrange
    mock_html_tag = MockHtmlTag()

    # Act & Assert
    with pytest.raises(expected_exception, match=expected_message):
        CompositeSemanticElement(mock_html_tag, (), inner_elements)


def test_composite_semantic_element_setter_valid_transformation(
    inner_elements_with_composite,
):
    """Test if inner_elements can be set when they have a valid transformation history."""
    # Arrange
    mock_html_tag = MockHtmlTag()
    element = CompositeSemanticElement(mock_html_tag, (), inner_elements_with_composite)

    # Act & Assert
    element.inner_elements = inner_elements_with_composite
    assert element.inner_elements == inner_elements_with_composite


def test_create_from_element_source_valid_inner_elements(default_inner_elements):
    """Test create_from_element() with valid inner elements."""
    # Arrange
    shared_mock = Mock()
    other = AbstractSemanticElement(shared_mock, ())

    # Act
    converted = CompositeSemanticElement.create_from_element(
        other,
        inner_elements=default_inner_elements,
    )

    # Assert
    assert isinstance(converted, CompositeSemanticElement)
    assert converted.inner_elements == default_inner_elements
    assert converted.html_tag == shared_mock


@pytest.mark.parametrize(
    "inner_elements, expected_exception, expected_message",
    [
        (None, ValueError, "inner_elements cannot be None or empty."),
        ((), ValueError, "inner_elements cannot be None or empty."),
    ],
)
def test_composite_semantic_element_setter_invalid_inner_elements(
    inner_elements_with_composite, inner_elements, expected_exception, expected_message
):
    """Test setting inner_elements to None or an empty tuple."""
    # Arrange
    mock_html_tag = MockHtmlTag()
    element = CompositeSemanticElement(mock_html_tag, (), inner_elements_with_composite)

    # Act & Assert
    with pytest.raises(expected_exception, match=expected_message):
        element.inner_elements = inner_elements


def test_composite_semantic_element_setter_mixed_transformation(
    inner_elements_with_composite, default_inner_elements
):
    """Test if setting inner_elements fails when they have a mixed transformation history."""
    # Arrange
    mock_html_tag = MockHtmlTag()
    element = CompositeSemanticElement(mock_html_tag, (), inner_elements_with_composite)

    mixed_inner_elements = inner_elements_with_composite + default_inner_elements

    # Act & Assert
    with pytest.raises(
        ValueError,
        match="Transformation history does not contain an instance of CompositeSemanticElement.",
    ):
        element.inner_elements = mixed_inner_elements
