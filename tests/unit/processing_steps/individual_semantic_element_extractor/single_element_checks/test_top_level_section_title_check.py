from unittest.mock import Mock

import bs4
import pytest

from sec_parser.processing_engine.html_tag import HtmlTag
from sec_parser.processing_steps.individual_semantic_element_extractor.single_element_checks.top_level_section_title_check import (
    TopLevelSectionTitleCheck,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)


class SemanticElement(AbstractSemanticElement):
    pass


@pytest.mark.parametrize(
    ("name", "html", "root_tag", "expected"),
    tests := [
        (
            "simple",
            "<div><p>Item 1</p><p>Hello World</p></div>",
            "div",
            False,
        ),
        (
            "AMC/0001411579-23-000057",
            """
                <div style="clear:both;max-width:100%;position:relative;">
                    <a id="_8b2a5540_cdbd_489b_a305_ea6dafa574a9"></a>
                    <a id="Item5OtherInformation_644562"></a>
                    <p style="font-family:'Times New Roman','Times','serif';font-size:10pt;margin:0pt 0pt 10pt 0pt;">
                        <b style="font-weight:bold;">Item</b>
                        <b style="font-weight:bold;white-space:pre-wrap;">5.  Other Information</b>
                    </p>
                    <p style="font-family:'Times New Roman','Times','serif';font-size:10pt;margin:0pt 0pt 10pt 0pt;">
                        <b style="font-weight:bold;background:#ffffff;">Rule 10b5-1 Trading Arrangements</b>
                    </p>
                    <p style="font-family:'Times New Roman','Times','serif';font-size:10pt;text-indent:40.5pt;margin:0pt 0pt 10pt 0pt;">
                        In the second quarter of 2023, no director or officer (as defined in Exchange Act Rule 16a-1(f)) of AMC
                        <ix:nonnumeric contextref="Duration_4_1_2023_To_6_30_2023_hVpn8aBFa0u0EiL3bnbnqw" format="ixt:booleanfalse" id="Narr_DDb55mYO1UCUO21UBpIfXg" name="ecd:NonRule10b51ArrAdoptedFlag">
                            <ix:nonnumeric contextref="Duration_4_1_2023_To_6_30_2023_hVpn8aBFa0u0EiL3bnbnqw" format="ixt:booleanfalse" id="Narr_WLk2K_58d0OJEKGusAiH-w" name="ecd:Rule10b51ArrAdoptedFlag">
                                adopted
                            </ix:nonnumeric>
                        </ix:nonnumeric>
                        or
                        <ix:nonnumeric contextref="Duration_4_1_2023_To_6_30_2023_hVpn8aBFa0u0EiL3bnbnqw" format="ixt:booleanfalse" id="Narr_uzpltLSsrUaahdFLeWXKjA" name="ecd:NonRule10b51ArrTrmntdFlag">
                            <ix:nonnumeric contextref="Duration_4_1_2023_To_6_30_2023_hVpn8aBFa0u0EiL3bnbnqw" format="ixt:booleanfalse" id="Narr_CjUadjuEj0afgT5uiUwSPg" name="ecd:Rule10b51ArrTrmntdFlag">
                                terminated
                            </ix:nonnumeric>
                        </ix:nonnumeric>
                        a Rule 10b5-1 trading arrangement or non-Rule 10b5-1 trading arrangement for the purchase or sale of securities of the Company, within the meaning of Item 408 of Regulation S-K.
                    </p>
                </div>
            """,
            "div",
            False,
        ),
    ],
    ids=[k[0] for k in tests],
)
def test_top_level_section_title_check(name, html, root_tag, expected):
    # Arrange
    bs4_tag = bs4.BeautifulSoup(html, "lxml").find(root_tag)
    assert isinstance(bs4_tag, bs4.Tag)
    html_tag = SemanticElement(HtmlTag(bs4_tag))
    check = TopLevelSectionTitleCheck()

    # Act
    actual = check.contains_single_element(html_tag)

    # Assert
    assert actual is expected
