from unittest.mock import Mock

import pytest

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    InvalidLevelError,
)


class DummyElement(AbstractLevelElement):
    pass


def test_invalid_level_raises():
    # Arrange
    invalid_level = -1

    # Act & Assert
    with pytest.raises(InvalidLevelError):
        DummyElement(Mock(), level=invalid_level)
