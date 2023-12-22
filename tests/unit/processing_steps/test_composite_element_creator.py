import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_steps.individual_semantic_element_extractor.individual_semantic_element_extractor import (
    IndividualSemanticElementExtractor,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import NotYetClassifiedElement
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "purely_text",
            """
                    <div>
                    <p>Some</p>
                    <p>Text</p>
                    </div>
                """,
            [
                {
                    "type": NotYetClassifiedElement,
                    "tag": "div",
                },
            ],
        ),
        (
            "nested",
            """
                    <div>
                        <table></table>
                        <div>
                            <table></table>
                            <p>text</p>
                        </div>
                    </div>
                """,
            [
                {
                    "type": CompositeSemanticElement,
                    "tag": "div",
                    "inner_elements": [
                        {
                            "type": NotYetClassifiedElement,
                            "tag": "table",
                        },
                        {
                            "type": CompositeSemanticElement,
                            "tag": "div",
                            "inner_elements": [
                                {
                                    "type": NotYetClassifiedElement,
                                    "tag": "table",
                                },
                                {
                                    "type": NotYetClassifiedElement,
                                    "tag": "p",
                                },
                            ],
                        },
                    ],
                },
            ],
        ),
        (
            "text_and_table",
            """
                    <div style="color:red;">
                        <div id="foo">
                            <p>Some</p>
                        </div>
                        <table>Text</table>
                        <div id="bar">
                            <table>Text</table>
                        </div>
                    </div>
                """,
            [
                {
                    "type": CompositeSemanticElement,
                    "tag": "div",
                    "inner_elements": [
                        {
                            "type": NotYetClassifiedElement,
                            "tag": "div",
                        },
                        {
                            "type": NotYetClassifiedElement,
                            "tag": "table",
                        },
                        {
                            "type": NotYetClassifiedElement,
                            "tag": "div",
                        },
                    ],
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_with_real_data(name, html_str, expected_elements):
    # Arrange
    sec_parser = Edgar10QParser(
        get_steps=lambda: [
            step
            for step in Edgar10QParser().get_default_steps()
            if isinstance(step, IndividualSemanticElementExtractor)
        ],
    )

    # Act
    processed_elements = sec_parser.parse(
        html_str, unwrap_elements=False, include_irrelevant_elements=True
    )

    # Assert
    assert_elements(processed_elements, expected_elements)
