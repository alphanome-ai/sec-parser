import pytest

from sec_parser import TextElement
from sec_parser.processing_steps import TextParsingStep
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    IrrelevantElement,
    TextElement,
)
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
    [
        (
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
                        {"type": EmptyElement, "tag": "p"},
                    ],
                },
                {"type": TextElement, "tag": "div"},
            ],
        ),
    ],
)
def test_text_step(html_str, expected_elements):
    """
    test_text_step test checks that the TextParsingStep can successfully transform
    a list of semantic elements returned by `parse_initial_semantic_elements`.
    """
    # Arrange
    elements = parse_initial_semantic_elements(html_str)
    step = TextParsingStep()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
