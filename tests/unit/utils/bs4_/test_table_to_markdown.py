import bs4
import pytest

from sec_parser.utils.bs4_.table_to_markdown import TableToMarkdown
from tests.unit.utils.bs4_._data_html_tables import (
    TABLE_10Q_CP_0000016875_20_000032__001,
)


@pytest.mark.parametrize(
    ("name", "html", "expected"),
    tests := [
        (
            "simple",
            """
            <table>
                <tr>
                    <th>Header 1</th>
                </tr>
                <tr>
                    <td>Cell 1</td>
                </tr>
            </table>
            """,
            "| Header 1 |\n|---|\n| Cell 1 |",
        ),
        (
            "10Q_CP_0000016875_20_000032",
            TABLE_10Q_CP_0000016875_20_000032__001,
            "| | | | | | | For the three months ended September 30 | | | | | | For the nine months ended September 30 |\n| (in millions of Canadian dollars) | | | 2020 | | | 2019 | | | 2020 | | | 2019 |\n| Net income | $ | 598 | | $ | 618 | | $ | 1642 | | $ | 1776 | |\n| Net gain (loss) in foreign currency translation adjustments, net of hedging activities | | 16 | | | (8 | ) | | (18 | ) | | 23 | |\n| Change in derivatives designated as cash flow hedges | | 3 | | | 2 | | | 6 | | | 8 | |\n| Change in pension and post-retirement defined benefit plans | | 44 | | | 20 | | | 134 | | | 61 | |\n| Other comprehensive income before income taxes | | 63 | | | 14 | | | 122 | | | 92 | |\n| Income tax (expense) recovery on above items | | (29 | ) | | 3 | | | (16 | ) | | (41 | ) |\n| Other comprehensive income (Note 7) | | 34 | | | 17 | | | 106 | | | 51 | |\n| Comprehensive income | $ | 632 | | $ | 635 | | $ | 1748 | | $ | 1827 | |",
        ),
    ],
    ids=[v[0] for v in tests],
)
def test_has_tag_children(name, html, expected):
    # Arrange
    p = bs4.BeautifulSoup(html, "lxml")
    assert isinstance(p, bs4.Tag)
    converter = TableToMarkdown(p)

    # Act
    result = converter.convert()

    # Assert
    assert result == expected
