import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_steps.composite_element_creator import (
    CompositeElementCreator,
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
    ],
    ids=[v[0] for v in values],
)
def test_with_real_data(name, html_str, expected_elements):
    sec_parser = Edgar10QParser(lambda: [CompositeElementCreator()])

    # Act
    processed_elements = sec_parser.parse(html_str, unwrap_elements=False)

    # Assert
    assert_elements(processed_elements, expected_elements)
