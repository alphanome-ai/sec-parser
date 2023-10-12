from unittest.mock import patch

import pytest

from sec_parser import TextElement
from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("html_str", "unwrap_elements", "expected_elements"),
    [
        (
            html_str := """
                <p>Hello world</p>
            """,
            False,
            expected_elements := [
                {"type": TextElement, "tag": "p"},
            ],
        ),
        (
            html_str,
            True,
            expected_elements,
        ),
    ],
)
def test_smoke_test(html_str, unwrap_elements, expected_elements):
    # Arrange
    sec_parser = Edgar10QParser()

    with patch(
        "sec_parser.semantic_elements.composite_semantic_element.CompositeSemanticElement.unwrap_elements",
        wraps=CompositeSemanticElement.unwrap_elements,
    ) as mock_unwrap:
        # Act
        processed_elements = sec_parser.parse(html_str, unwrap_elements=unwrap_elements)

        # Assert
        assert_elements(processed_elements, expected_elements)
        if unwrap_elements:
            mock_unwrap.assert_called()
        else:
            mock_unwrap.assert_not_called()
