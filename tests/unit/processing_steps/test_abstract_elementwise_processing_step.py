from __future__ import annotations

from unittest.mock import Mock

import bs4
import pytest

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementwiseProcessingContext,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class MockSemanticElement(AbstractSemanticElement):
    pass


class AnotherMockSemanticElement(AbstractSemanticElement):
    pass


class ProcessingStep(AbstractElementwiseProcessingStep):
    def __init__(
        self,
        *,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )
        self.seen_elements: list[AbstractSemanticElement] = []

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseProcessingContext,
    ) -> AbstractSemanticElement:
        self.seen_elements.append(element)
        return element


def test_process_skip_due_to_types_to_process():
    """Test that elements not in 'types_to_process' are skipped."""
    # Arrange
    types_to_process: set[type[AbstractSemanticElement]] = {MockSemanticElement}
    step = ProcessingStep(types_to_process=types_to_process)
    element1 = MockSemanticElement(Mock(), ())
    element2 = AnotherMockSemanticElement(Mock(), ())
    input_elements = [element1, element2]

    # Act
    processed_elements = step.process(input_elements)

    # Assert
    assert step.seen_elements == [element1]
    assert processed_elements == input_elements


def test_process_skip_due_to_types_to_exclude():
    """Test that elements in 'types_to_exclude' are skipped."""
    # Arrange
    types_to_exclude: set[type[AbstractSemanticElement]] = {MockSemanticElement}
    step = ProcessingStep(types_to_exclude=types_to_exclude)
    element1 = MockSemanticElement(Mock(), ())
    element2 = AnotherMockSemanticElement(Mock(), ())
    input_elements = [element1, element2]

    # Act
    processed_elements = step.process(input_elements)

    # Assert
    assert step.seen_elements == [element2]
    assert processed_elements == input_elements


def test_process_skip_due_to_both_types_to_process_and_types_to_exclude():
    """
    Test that elements not in 'types_to_process' are skipped and
    then the elements in 'types_to_exclude' are also skipped.
    """
    # Arrange
    types_to_process: set[type[AbstractSemanticElement]] = {
        MockSemanticElement,
        AnotherMockSemanticElement,
    }
    types_to_exclude: set[type[AbstractSemanticElement]] = {AnotherMockSemanticElement}

    step = ProcessingStep(
        types_to_process=types_to_process,
        types_to_exclude=types_to_exclude,
    )
    element1 = MockSemanticElement(Mock(), ())
    element2 = AnotherMockSemanticElement(Mock(), ())
    input_elements = [element1, element2]

    # Act
    processed_elements = step.process(input_elements)

    # Assert
    assert step.seen_elements == [element1]
    assert processed_elements == input_elements
    assert processed_elements == input_elements
