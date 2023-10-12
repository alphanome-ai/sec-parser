import pytest

from sec_parser import TextElement
from sec_parser.processing_engine.core import Edgar10QParser
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
def test_smoke_test(html_str, expected_elements):
    # Arrange
    sec_parser = Edgar10QParser()

    # Act
    processed_elements = sec_parser.parse(html_str)

    # Assert
    assert_elements(processed_elements, expected_elements)
