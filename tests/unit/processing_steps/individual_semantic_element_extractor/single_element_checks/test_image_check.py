from unittest.mock import Mock
import bs4
import pytest

from sec_parser.semantic_elements.abstract_semantic_element import AbstractSemanticElement
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.image_check import ImageCheck


def test_contains_single_element_with_img_tag():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "img"
    check = ImageCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is True
    

def test_contains_single_element_with_multiple_img_tags():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "div"
    element.html_tag.count_tags.side_effect = lambda tag_name: 2 if tag_name == 'img' else 0
    check = ImageCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is False


def test_contains_single_element_with_text_and_img_tag():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "div"
    element.html_tag.count_tags.side_effect = lambda tag_name: 1 if tag_name == 'img' else 0
    element.html_tag.text = "Some text"
    check = ImageCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is False


def test_contains_single_element_with_other_tags():
    # Arrange
    element = AbstractSemanticElement(Mock())
    element.html_tag.name = "div"
    element.html_tag.count_tags.side_effect = lambda tag_name: 0 if tag_name == 'img' else 2
    element.html_tag.text = ""
    check = ImageCheck()

    # Act
    actual = check.contains_single_element(element)

    # Assert
    assert actual is None