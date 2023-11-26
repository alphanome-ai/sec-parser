from unittest.mock import Mock

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    ElementProcessingContext,
)
from sec_parser.processing_steps.empty_element_classifier import (
    EmptyElementClassifier,
    InvalidIterationError,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    IrrelevantElement,
    TextElement,
)
from sec_parser.semantic_elements.title_element import TitleElement
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
def test_irrelevant_element_classifier(name, html_str, expected_elements):
    # Arrange
    def get_steps():
        default = Edgar10QParser().get_default_steps()
        return list(default)

    sec_parser = Edgar10QParser(get_steps)

    # Act
    processed_elements = sec_parser.parse(html_str, unwrap_elements=False)

    # Assert
    assert_elements(processed_elements, expected_elements)
