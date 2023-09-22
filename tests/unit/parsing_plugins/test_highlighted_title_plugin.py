import pytest

from sec_parser import TextElement
from sec_parser.parsing_plugins import TextPlugin
from sec_parser.parsing_plugins.highlighted_text_plugin import \
    HighlightedTextPlugin
from sec_parser.parsing_plugins.title_plugin import TitlePlugin
from sec_parser.semantic_elements.semantic_elements import (
    IrrelevantElement, TextElement, TitleElement, UndeterminedElement)
from tests.unit.parsing_plugins._utils import (SpecialElement, assert_elements,
                                               get_elements_from_html)


@pytest.mark.parametrize(
    "html_str, expected_elements",
    [
        (   # From Apple 10-Q
            """ 
                <div style="margin-top:18pt;text-align:justify">
                    <span style="color:#000000;font-family:'Helvetica',sans-serif;font-size:9pt;font-weight:700;line-height:120%">
                        Available Information
                    </span>
                </div>
                <div style="margin-top:6pt;text-align:justify">
                    <span style="color:#000000;font-family:'Helvetica',sans-serif;font-size:9pt;font-weight:400;line-height:120%">
                        The Company periodically provides certain information for investors on its corporate website
                    </span>
                </div>
            """,
            [
                {"type": TitleElement, "tag": "div"},
                {"type": UndeterminedElement, "tag": "div"},
            ],
        ),
    ],
)
def test_title_plugin(html_str, expected_elements):
    """
    This test checks that the HighlightedTextPlugin and TitlePlugin
    can successfully transform a list of semantic elements returned by 
    `get_elements_from_html`. These elements can be of type 
    `UndeterminedElement` or `SpecialElement`.
    """

    # Arrange
    elements = get_elements_from_html(html_str)
    
    highlighter_plugin = HighlightedTextPlugin()
    title_plugin = TitlePlugin()

    # Act
    elements = highlighter_plugin.transform(elements)
    elements = title_plugin.transform(elements)

    # Assert
    assert_elements(elements, expected_elements)
