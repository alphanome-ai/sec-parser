import pytest

from sec_parser.processing_steps.abstract_classes.abstract_element_batch_processing_step import (
    AbstractElementBatchProcessingStep,
)
from sec_parser.processing_steps.abstract_classes.processing_context import (
    ElementProcessingContext,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


class Passthrough(AbstractElementBatchProcessingStep):
    def _process_elements(
        self,
        elements: list[AbstractSemanticElement],
        _: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        return elements


class DivTagPruner(AbstractElementBatchProcessingStep):
    def _process_elements(
        self,
        elements: list[AbstractSemanticElement],
        _: ElementProcessingContext,
    ) -> list[AbstractSemanticElement]:
        return [e for e in elements if e.html_tag.name != "div"]


@pytest.mark.parametrize(
    ("name", "cls", "html_str", "expected_elements"),
    values := [
        (
            "passthrough",
            Passthrough,
            """
                <p>1</p>
                <composite>
                    <div><i>2</i></div>
                    <p></p>
                </composite>
                <div>
                    <p>3</p>
                    <p>4</p>
                </div>
            """,
            [
                {"type": NotYetClassifiedElement, "tag": "p"},
                {
                    "type": CompositeSemanticElement,
                    "tag": "composite",
                    "children": [
                        {"type": NotYetClassifiedElement, "tag": "div"},
                        {"type": NotYetClassifiedElement, "tag": "p"},
                    ],
                },
                {"type": NotYetClassifiedElement, "tag": "div"},
            ],
        ),
        (
            "div_tag_pruner",
            DivTagPruner,
            """
                <p>1</p>
                <composite>
                    <div><i>2</i></div>
                    <p></p>
                </composite>
                <div>
                    <p>3</p>
                    <p>4</p>
                </div>
            """,
            [
                {"type": NotYetClassifiedElement, "tag": "p"},
                {
                    "type": CompositeSemanticElement,
                    "tag": "composite",
                    "children": [
                        {"type": NotYetClassifiedElement, "tag": "p"},
                    ],
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_batch_processing_step(name, cls, html_str, expected_elements):
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = cls()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
