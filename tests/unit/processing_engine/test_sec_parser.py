from unittest.mock import patch

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("name", "html_str", "unwrap_elements", "expected_elements"),
    values := [
        (
            "unwrap=false",
            html_str := """
                <span style="font-weight:bold">
                    Item 1
                </span>
            """,
            False,
            expected_elements := [
                {"type": TopLevelSectionTitle, "tag": "span"},
            ],
        ),
        (
            "unwrap=true",
            html_str,
            True,
            expected_elements,
        ),
    ],
    ids=[v[0] for v in values],
)
def test_smoke_test(name, html_str, unwrap_elements, expected_elements):
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
