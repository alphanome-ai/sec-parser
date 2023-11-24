from unittest.mock import patch

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.processing_log import LogItem
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.title_element import TitleElement
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("name", "html_str", "unwrap_elements", "expected_elements"),
    values := [
        (
            "unwrap=false",
            html_str := """
                <span style="font-weight:bold">
                    Hello
                </span>
            """,
            False,
            expected_elements := [
                {"type": TitleElement, "tag": "span"},
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


@pytest.mark.parametrize(
    ("name", "html_str", "expected_processing_log"),
    values := [
        (
            "simple",
            "<div>Hello World.</div>",
            (
                LogItem(
                    origin="TextClassifier",
                    payload={"cls_name": "TextElement"},
                ),
            ),
        ),
    ],
    ids=[v[0] for v in values],
)
def test_transformation_history(name, html_str, expected_processing_log):
    # Arrange
    sec_parser = Edgar10QParser()

    # Act
    processed_elements = sec_parser.parse(html_str)
    processing_log = processed_elements[0].processing_log.get_items()

    # Assert
    assert (
        len(processed_elements) == 1
    )  # For simplicity, while crafting `html_str` make sure it always returns single element.
    assert processing_log == expected_processing_log
