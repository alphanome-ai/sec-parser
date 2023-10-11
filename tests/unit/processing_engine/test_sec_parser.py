import pytest

from sec_parser import TextElement
from sec_parser.processing_engine.sec_parser import SecParser
from sec_parser.processing_steps import TextParsingStep
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
    [
        (
            """
            <p>Hello world</p>
            """,
            [
                {"type": TextElement, "tag": "p"},
            ],
        ),
    ],
)
def test_sec_parser(html_str, expected_elements):
    # Arrange
    sec_parser = SecParser()

    # Act
    processed_elements = sec_parser.parse(html_str)

    # Assert
    assert_elements(processed_elements, expected_elements)
