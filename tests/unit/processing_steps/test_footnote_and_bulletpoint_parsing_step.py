import pytest

from sec_parser.processing_steps.footnote_and_bulletpoint_parsing_step import (
    FootnoteAndBulletpointParsingStep,
)
from sec_parser.semantic_elements.semantic_elements import BulletpointTextElement
from tests.unit.processing_steps._utils import assert_elements, get_elements_from_html


@pytest.mark.parametrize(
    ("html_str", "expected_elements"),
    [
        (
            """
            <div style="margin-top:6pt;padding-left:36pt;text-align:justify;text-indent:-18pt">
                <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%">
                    •
                </span>
                <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%;padding-left:14.5pt">
                    Parent bulletpoint
                </span>
            </div>
            <div style="margin-top:6pt;padding-left:72pt;text-align:justify;text-indent:-18pt">
                <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%">
                ◦
                </span>
                <span style="color:#000000;font-family:'Arial',sans-serif;font-size:10pt;font-weight:400;line-height:120%;padding-left:14.46pt">
                Child bulletpoint
                </span>
            </div>
            """,
            [
                {
                    "type": BulletpointTextElement,
                    "tag": "div",
                    "fields": {"level": 1},
                },
                {
                    "type": BulletpointTextElement,
                    "tag": "div",
                    "fields": {"level": 2},
                },
            ],
        ),
    ],
)
def test_footnote_and_bulletpoint_step(html_str, expected_elements):
    """
    test_footnote_and_bulletpoint_step test checks that the FootnoteAndBulletpointParsingStep can successfully transform a list of
    semantic elements returned by `get_elements_from_html`. These elements can be
    of type `UndeterminedElement` or `SpecialElement`.
    """
    # Arrange
    elements = get_elements_from_html(html_str)
    step = FootnoteAndBulletpointParsingStep()

    # Act
    processed_elements = step.process(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
