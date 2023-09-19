import pytest
from sec_parser import TextElement
from sec_parser.parsing_plugins.footnote_and_bulletpoint_plugin import (
    FootnoteAndBulletpointPlugin,
)
from tests.unit.parsing_plugins._utils import (
    get_elements_from_html,
    UndeterminedElement,
    SpecialElement,
    assert_elements,
)
from sec_parser.parsing_plugins import TextPlugin
from sec_parser.semantic_elements.semantic_elements import (
    BulletpointTextElement,
    IrrelevantElement,
    TextElement,
)


@pytest.mark.parametrize(
    "html_str, expected_elements",
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
def test_footnote_and_bulletpoint_plugin(html_str, expected_elements):
    # Arrange
    elements = get_elements_from_html(html_str)
    plugin = FootnoteAndBulletpointPlugin()

    # Act
    processed_elements = plugin.transform(elements)

    # Assert
    assert_elements(processed_elements, expected_elements)
