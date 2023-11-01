from unittest.mock import Mock
import bs4
import pytest

from sec_parser.semantic_elements.abstract_semantic_element import AbstractSemanticElement
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.table_check import TableCheck

def test_table_check():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "table"
    check = TableCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is True