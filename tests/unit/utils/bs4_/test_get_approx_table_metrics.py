import bs4
import pytest

from sec_parser.utils.bs4_.approx_table_metrics import (
    ApproxTableMetrics,
    get_approx_table_metrics,
)
from tests.unit.utils.bs4_._data_html_tables import (
    TABLE_10Q_AAPL_000032019323000077__001,
)

test_cases = [TABLE_10Q_AAPL_000032019323000077__001]


@pytest.mark.parametrize(
    ("name", "html", "expected"),
    values := [
        (
            "table_tag_at_root",
            "<table><tr><td>HELLO</td></tr><tr><td>456</td></tr></table>",
            ApproxTableMetrics(rows=2, numbers=1),
        ),
        (
            "10Q_AAPL_000032019323000077",
            TABLE_10Q_AAPL_000032019323000077__001,
            ApproxTableMetrics(
                rows=13,
                numbers=44,
            ),
        ),
    ],
    ids=[v[0] for v in values],
)
def test_get_table_metrics(name: str, html: str, expected: ApproxTableMetrics) -> None:
    soup = bs4.BeautifulSoup(html, "lxml")
    root = next(soup.html.body.children)

    # Act
    actual = get_approx_table_metrics(root)

    # Assert
    assert actual == expected, f"{name}: {actual} != {expected}"
