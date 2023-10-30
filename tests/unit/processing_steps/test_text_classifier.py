import pytest

from sec_parser import TextElement
from sec_parser.processing_steps import TextClassifier
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
)
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "simple",
            """
                <p>a</p>
                <composite>
                    <div><i>b</i></div>
                    <p></p>
                </composite>
                <div>
                    <p>c</p>
                    <p>d</p>
                </div>
            """,
            [
                {"type": TextElement, "tag": "p"},
                {
                    "type": CompositeSemanticElement,
                    "tag": "composite",
                    "children": [
                        {"type": TextElement, "tag": "div"},
                        {"type": NotYetClassifiedElement, "tag": "p"},
                    ],
                },
                {"type": TextElement, "tag": "div"},
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_text_classifier(name, html_str, expected_elements):
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = TextClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
