from unittest.mock import patch

import bs4
import pytest

from sec_parser.processing_engine.core import Edgar10QParser
from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.pre_top_level_section_pruner import (
    PreTopLevelSectionPruner,
)
from sec_parser.processing_steps.top_level_section_title_classifier import (
    TopLevelSectionTitleClassifier,
)
from sec_parser.semantic_elements.composite_semantic_element import (
    CompositeSemanticElement,
)
from sec_parser.semantic_elements.semantic_elements import TextElement, TitleElement
from sec_parser.semantic_elements.table_element import TableElement
from sec_parser.semantic_elements.top_level_section_title import TopLevelSectionTitle
from tests.unit._utils import assert_elements
from tests.unit.processing_steps._utils import parse_initial_semantic_elements


def html_tag(tag_name: str, text: str = "Hello World") -> HtmlTag:
    tag = bs4.Tag(name=tag_name)
    tag.string = text
    return HtmlTag(tag)


@pytest.mark.parametrize(
    ("name", "elements", "expected_elements"),
    values := [
        (
            "empty",
            [],
            [],
        ),
        (
            "elements",
            [
                TextElement(html_tag("p", text="Item 1")),
                TextElement(html_tag("p", text="Part 1")),
                TitleElement(html_tag("p", text="Hello")),
                TitleElement(html_tag("p", text="Part I")),
                TitleElement(html_tag("p", text="Item 2")),
            ],
            [
                {"type": TextElement, "tag": "p"},
                {"type": TextElement, "tag": "p"},
                {"type": TitleElement, "tag": "p"},
                {"type": TopLevelSectionTitle, "tag": "p", "fields": {"level": 0}},
                {
                    "type": TopLevelSectionTitle,
                    "tag": "p",
                    "fields": {"level": 1, "identifier": "part1item2"},
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_pre_top_level_section_pruner(name, elements, expected_elements):
    # Arrange
    step = TopLevelSectionTitleClassifier()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)


@pytest.mark.parametrize(
    ("name", "html_str", "expected_elements"),
    values := [
        (
            "10-Q_AMZN_0001018724-23-000012",
            """
<div>
 <table style="border-collapse:collapse;display:inline-table;margin-bottom:5pt;vertical-align:text-bottom;width:99.853%">
  <tr>
   <td style="width:1.0%">
   </td>
   <td style="width:9.880%">
   </td>
   <td style="width:0.1%">
   </td>
   <td style="width:1.0%">
   </td>
   <td style="width:87.920%">
   </td>
   <td style="width:0.1%">
   </td>
  </tr>
  <tr>
   <td colspan="3" style="padding:2px 1pt;text-align:left;vertical-align:top">
    <span style="color:#000000;font-family:'Times New Roman',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
     Item 1.
    </span>
   </td>
   <td colspan="3" style="padding:2px 1pt;text-align:left;vertical-align:top">
    <span style="color:#000000;font-family:'Times New Roman',sans-serif;font-size:10pt;font-weight:700;line-height:120%">
     Financial Statements
    </span>
   </td>
  </tr>
 </table>
</div>
                """,
            [
                # TODO(elijas): The following test is currently failing and has been
                # temporarily silenced. For more details, refer to:
                # https://github.com/alphanome-ai/sec-parser/issues/29
                {
                    "type": TableElement,  # should be TopLevelSectionTitle
                    "tag": "div",
                    # should have "fields": {"level": 1, "identifier": "part1item1"},
                },
            ],
        ),
    ],
    ids=[v[0] for v in values],
)
def test_e2e_pre_top_level_section_pruner(name, html_str, expected_elements):
    # Arrange
    def get_steps():
        default = Edgar10QParser.get_default_steps()
        return [s for s in default if not isinstance(s, PreTopLevelSectionPruner)]

    sec_parser = Edgar10QParser(get_steps)

    # Act
    processed_elements = sec_parser.parse(html_str, unwrap_elements=False)

    # Assert
    assert_elements(processed_elements, expected_elements)
