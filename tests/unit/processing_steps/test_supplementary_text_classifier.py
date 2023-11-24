from unittest.mock import Mock

import bs4
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
from sec_parser.processing_steps.supplementary_text_classifier import (
    SupplementaryTextClassifier,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    ImageElement,
    IrrelevantElement,
    SupplementaryText,
    TextElement,
)
from sec_parser.semantic_elements.table_element.table_element import TableElement
from sec_parser.semantic_elements.title_element import TitleElement
from tests.unit._utils import assert_elements


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "10-Q_GOOG_0001652044-23-000070",
            """
<p>(Hello)</p>
<p>Notes to Financial Statements.</p>
<p>See Accompanying Notes.</p>
<p style="font-style: italic;">Italic Text.</p>
                """,
            [
                {
                    "type": SupplementaryText,
                    "tag": "p",
                },
                {
                    "type": SupplementaryText,
                    "tag": "p",
                },
                {
                    "type": SupplementaryText,
                    "tag": "p",
                },
                {
                    "type": SupplementaryText,
                    "tag": "p",
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_supplementary_element_classifier(name, html_str, expected_elements):
    # Arrange
    def get_steps():
        default = Edgar10QParser().get_default_steps()
        return list(default)

    sec_parser = Edgar10QParser(get_steps)

    # Act
    processed_elements = sec_parser.parse(html_str, unwrap_elements=False)

    # Assert
    assert_elements(processed_elements, expected_elements)


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


@pytest.mark.parametrize(
    ("name", "elements", "expected_elements"),
    values := [
        (
            "elements",
            [
                EmptyElement(html_tag("p", text="")),
            ],
            [
                {"type": EmptyElement, "tag": "p"},
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_with_synthetic_input(name, elements, expected_elements):
    # Arrange
    step = SupplementaryTextClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
