from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_steps.abstract_classes.abstract_processing_step import (
    AbstractProcessingStep,
    AlreadyProcessedError,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class DummyElement(AbstractSemanticElement):
    pass


class DummyProcessingStep(AbstractProcessingStep):
    def _process(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        return elements


def test_process_already_processed_raises_error():
    # Arrange
    elements: list[AbstractSemanticElement] = [DummyElement(Mock()) for _ in range(5)]
    step = DummyProcessingStep()

    # Act
    step.process(elements)

    # Assert
    with pytest.raises(
        AlreadyProcessedError,
        match="This Step instance has already processed a document",
    ):
        step.process(elements)
