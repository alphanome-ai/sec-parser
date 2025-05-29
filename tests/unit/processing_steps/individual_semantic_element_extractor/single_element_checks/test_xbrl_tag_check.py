from unittest.mock import Mock

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.xbrl_tag_check import (
    XbrlTagCheck,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


def test_contains_single_element_ix_tag() -> None:
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "ix"
    check = XbrlTagCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is False


def test_contains_single_element_ix_numeric_tag() -> None:
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "ix:numeric"
    check = XbrlTagCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is False
