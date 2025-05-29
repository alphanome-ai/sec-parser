from unittest.mock import Mock

from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.table_check import (
    TableCheck,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


def test_table_check() -> None:
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "table"
    check = TableCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is True
