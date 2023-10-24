import pytest

from sec_parser import TextElement
from sec_parser.processing_steps import TextClassifier
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
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
                <p>1</p>
                <section>
                    <div><i>2</i></div>
                    <p></p>
                </section>
                <div>
                    <p>3</p>
                    <p>4</p>
                </div>
            """,
            [
                {"type": TextElement, "tag": "p"},
                {
                    "type": CompositeSemanticElement,
                    "tag": "section",
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
