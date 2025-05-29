import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    TextElement,
)
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "simple",
            """
<p>hello</p>
<p></p>
                """,
            [
                {
                    "type": TextElement,
                    "tag": "p",
                },
                {
                    "type": EmptyElement,
                    "tag": "p",
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_irrelevant_element_classifier(name, html_str, expected_elements) -> None:
    # Arrange
    def get_steps():
        default = Edgar10QParser().get_default_steps()
        return list(default)

    sec_parser = Edgar10QParser(get_steps)

    # Act
    processed_elements = sec_parser.parse(
        html_str, unwrap_elements=False, include_irrelevant_elements=True,
    )

    # Assert
    assert_elements(processed_elements, expected_elements)
