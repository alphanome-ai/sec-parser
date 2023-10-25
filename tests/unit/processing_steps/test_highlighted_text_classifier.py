import pytest

from sec_parser.processing_steps.highlighted_text_classifier import (
    HighlightedTextClassifier,
)
from sec_parser.processing_steps.text_classifier import TextClassifier
from sec_parser.processing_steps.title_classifier import TitleClassifier
from sec_parser.semantic_elements.semantic_elements import (
    NotYetClassifiedElement,
    TextElement,
)
from sec_parser.semantic_elements.title_element import TitleElement
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "from Apple 10-Q",
            """
                <div style="margin-top:18pt;text-align:justify">
                    <span style="color:#000000;font-family:'Helvetica',sans-serif;font-size:9pt;font-weight:700;line-height:120%">
                        Available Information
                    </span>
                </div>
                <div style="margin-top:6pt;text-align:justify">
                    <span style="color:#000000;font-family:'Helvetica',sans-serif;font-size:9pt;font-weight:400;line-height:120%">
                        The Company periodically provides certain information for investors on its corporate website
                    </span>
                </div>
            """,
            [
                {"type": TitleElement, "tag": "div"},
                {"type": TextElement, "tag": "div"},
            ],
        ),
        (
            "bold",
            """
                <div>
                    <span style="font-weight:bold">
                        foo
                    </span>
                    <span style="font-weight:bold">
                        bar
                    </span>
                </div>
                <span style="font-weight:unknown">
                    baz
                </span>
                <p></p>
            """,
            [
                {"type": TitleElement, "tag": "div"},
                {"type": TextElement, "tag": "span"},
                {"type": NotYetClassifiedElement, "tag": "p"},
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_title_step(name, html_str, expected_elements):
    """
    test_title_step test checks that the HighlightedTextClassifier and TitleClassifier
    can successfully transform a list of semantic elements returned by
    `parse_initial_semantic_elements`.
    """
    # Arrange
    text_step = TextClassifier()
    highlight_step = HighlightedTextClassifier()
    title_step = TitleClassifier()
    elements = parse_initial_semantic_elements(html_str)
    elements = text_step.process(elements)
    elements = highlight_step.process(elements)

    # Act
    elements = title_step.process(elements)

    # Assert
    assert_elements(elements, expected_elements)
