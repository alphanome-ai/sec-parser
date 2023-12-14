from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
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


def test_to_dict():
    # Arrange
    tag = bs4.Tag(name="span")
    tag.string = "A" * 60

    # Act
    actual = DummyElement(HtmlTag(tag)).to_dict(include_previews=True)

    # Assert
    assert actual["cls_name"] == "DummyElement"


def test_repr():
    # Arrange
    tag = bs4.Tag(name="div")
    element = DummyElement(HtmlTag(tag))

    # Act
    repr_string = repr(element)

    # Assert
    assert repr_string == "DummyElement[L0]<div>"
