from unittest.mock import Mock

import pytest

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)

# Create a mock for HtmlTag
MockHtmlTag = Mock()


@pytest.fixture
def default_inner_elements():
    return [Mock(spec=AbstractSemanticElement) for _ in range(3)]


def test_composite_semantic_element_initialization_valid_inner_elements(
    default_inner_elements,
):
    """
    Test if a CompositeSemanticElement object can be successfully initialized
    with valid inner elements.
    """
    # Arrange
    mock_html_tag = MockHtmlTag()

    # Act
    element = CompositeSemanticElement(mock_html_tag, default_inner_elements)

    # Assert
    assert element.inner_elements == default_inner_elements
    assert element.html_tag == mock_html_tag


def test_composite_semantic_element_initialization_none_inner_elements():
    """
    Test if initializing CompositeSemanticElement with inner_elements
    as None raises a ValueError.
    """
    # Arrange
    mock_html_tag = MockHtmlTag()

    # Act & Assert
    with pytest.raises(ValueError, match="inner_elements cannot be None."):
        CompositeSemanticElement(mock_html_tag, None)


def test_composite_semantic_element_initialization_empty_inner_elements():
    """
    Test if initializing CompositeSemanticElement with an empty list
    for inner_elements raises a ValueError.
    """
    # Arrange
    mock_html_tag = MockHtmlTag()

    # Act & Assert
    with pytest.raises(ValueError, match="inner_elements cannot be empty."):
        CompositeSemanticElement(mock_html_tag, [])


def test_convert_from_source_valid_inner_elements(default_inner_elements):
    """
    Test if convert_from method can successfully convert from a source object
    with valid inner elements.
    """
    # Arrange
    mock_html_tag = MockHtmlTag()
    source = Mock(spec=AbstractSemanticElement)
    source.html_tag = mock_html_tag

    # Act
    converted = CompositeSemanticElement.convert_from(
        source, inner_elements=default_inner_elements
    )

    # Assert
    assert isinstance(converted, CompositeSemanticElement)
    assert converted.inner_elements == default_inner_elements
    assert converted.html_tag == mock_html_tag
