from unittest.mock import Mock

import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    ElementProcessingContext,
)
from sec_parser.processing_steps.irrelevant_element_classifier import (
    InvalidIterationError,
    IrrelevantElementClassifier,
)
from sec_parser.processing_steps.pre_top_level_section_pruner import (
    PreTopLevelSectionPruner,
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
            "10-Q_GOOG_0001652044-23-000070",
            """
<div style="margin-top:3pt;text-align:center">
 <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
  Alphabet Inc.
 </span>
</div>

<div style="text-align:center">
 <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
  CONSOLIDATED BALANCE SHEETS
 </span>
</div>

<p>some text</p>

<p></p>

<div style="margin-top:3pt;text-align:center">
 <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
  Alphabet Inc.
 </span>
</div>

<div style="text-align:center">
 <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
  FINANCIAL STATEMENTS
 </span>
</div>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
<p>repeating</p>
                """,
            [
                {
                    "type": IrrelevantElement,
                    "tag": "div",
                },
                {
                    "type": TitleElement,
                    "tag": "div",
                },
                {
                    "type": TextElement,
                    "tag": "p",
                },
                {
                    "type": EmptyElement,
                    "tag": "p",
                },
                {
                    "type": IrrelevantElement,
                    "tag": "div",
                },
                {
                    "type": TitleElement,
                    "tag": "div",
                },
                *[
                    {
                        "type": IrrelevantElement,
                        "tag": "p",
                    },
                ]
                * 10,
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_irrelevant_element_classifier(name, html_str, expected_elements):
    # Arrange
    def get_steps():
        default = Edgar10QParser().get_default_steps()
        return [s for s in default if not isinstance(s, PreTopLevelSectionPruner)]

    sec_parser = Edgar10QParser(get_steps)

    # Act
    processed_elements = sec_parser.parse(html_str, unwrap_elements=False)

    # Assert
    assert_elements(processed_elements, expected_elements)

    # Assert
    assert_elements(processed_elements, expected_elements)


def test_process_element_raises_value_error():
    classifier = IrrelevantElementClassifier()
    context = ElementProcessingContext(False, 2)  # Invalid iteration
    element = AbstractSemanticElement(
        Mock(spec=HtmlTag),
    )  # Assume this is a valid element

    with pytest.raises(InvalidIterationError):
        classifier._process_element(element, context)
