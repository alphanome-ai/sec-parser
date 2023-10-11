import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_processing_step import (
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
    # Arrange: Create a list of dummy elements and a dummy processing step
    elements: list[AbstractSemanticElement] = [
        DummyElement(html_tag=HtmlTag(bs4.Tag(name="p"))) for _ in range(5)
    ]
    step = DummyProcessingStep()

    # Act: Call process once (this should not raise an error)
    step.process(elements)

    # Assert: Calling process a second time should raise an error
    with pytest.raises(
        AlreadyProcessedError, match="This Step instance has already processed"
    ):
        step.process(elements)
