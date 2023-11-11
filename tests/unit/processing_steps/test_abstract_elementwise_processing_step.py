from __future__ import annotations

from unittest.mock import Mock

import pytest
from loguru import logger

from sec_parser.exceptions import SecParserError, SecParserValueError
from sec_parser.processing_engine.processing_log import LogItemOrigin
from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    MODULE_LOGGER_NAME,
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
    ErrorWhileProcessingElement,
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
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        self.seen_elements.append(element)
        return element


class ErrorRaisingProcessingStep(AbstractElementwiseProcessingStep):
    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        raise SecParserError


def test_process_skip_due_to_types_to_process():
    """Test that elements not in 'types_to_process' are skipped."""
    # Arrange
    types_to_process: set[type[AbstractSemanticElement]] = {MockSemanticElement}
    step = ProcessingStep(types_to_process=types_to_process)
    element1 = MockSemanticElement(Mock())
    element2 = AnotherMockSemanticElement(Mock())
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
    element1 = MockSemanticElement(Mock())
    element2 = AnotherMockSemanticElement(Mock())
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
    element1 = MockSemanticElement(Mock())
    element2 = AnotherMockSemanticElement(Mock())
    input_elements = [element1, element2]

    # Act
    processed_elements = step.process(input_elements)

    # Assert
    assert step.seen_elements == [element1]
    assert processed_elements == input_elements
    assert processed_elements == input_elements


def test_error_while_processing_element():
    # Arrange
    input_elements = [MockSemanticElement(Mock())]
    step = ErrorRaisingProcessingStep()

    # Act
    logger.disable(MODULE_LOGGER_NAME)
    elements = step.process(input_elements)
    logger.enable(MODULE_LOGGER_NAME)

    # Assert
    assert isinstance(elements[0], ErrorWhileProcessingElement)


def test_error_while_processing_element_with_no_error():
    # Arrange
    element = MockSemanticElement(Mock())

    # Act & Assert
    with pytest.raises(SecParserValueError):
        ErrorWhileProcessingElement.create_from_element(
            element,
            error=None,
            log_origin=Mock(spec=LogItemOrigin),
        )
