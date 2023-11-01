import pytest

from sec_parser.processing_steps.individual_semantic_element_extractor.individual_semantic_element_extractor import IndividualSemanticElementExtractor
from sec_parser.exceptions import SecParserValueError


def test_init_with_no_checks():
    # Arrange
    get_checks = None

    # Act & Assert
    with pytest.raises(SecParserValueError):
        IndividualSemanticElementExtractor(get_checks=get_checks)