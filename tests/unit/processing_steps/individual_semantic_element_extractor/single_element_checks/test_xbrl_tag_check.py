from unittest.mock import Mock
import bs4
import pytest

from sec_parser.semantic_elements.abstract_semantic_element import AbstractSemanticElement
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.xbrl_tag_check import XbrlTagCheck


def test_contains_single_element():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "ix"
    check = XbrlTagCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is False #TODO(@INF800): Verify if `True` or `False` is expected.