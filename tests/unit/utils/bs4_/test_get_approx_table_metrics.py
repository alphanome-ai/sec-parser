import bs4
import pytest

from sec_parser.utils.bs4_.approx_table_metrics import (
    ApproxTableMetrics,
    MultipleTablesFoundError,
    NoTableFoundError,
    get_approx_table_metrics,
)
from tests.unit.utils.bs4_._data_test_get_approx_table_metrics import (
    AAPL_10Q_000032019323000077_TABLE,
)

test_cases = [AAPL_10Q_000032019323000077_TABLE]


@pytest.mark.parametrize(
    ("name", "html", "expected"),
    values := [
        (
            "table_tag_at_root",
            "<table><tr><td>HELLO</td></tr><tr><td>456</td></tr></table>",
            ApproxTableMetrics(rows=2, numbers=1),
        ),
        (
            "AAPL_10Q_000032019323000077",
            AAPL_10Q_000032019323000077_TABLE,
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


@pytest.mark.parametrize(
    ("html", "exception"),
    [
        ("<div><p>No table here.</p></div>", NoTableFoundError),
        (
            "<div><table><tr><td>1</td></tr></table><table><tr><td>2</td></tr></table></div>",
            MultipleTablesFoundError,
        ),
    ],
)
def test_table_errors(html: str, exception: type[Exception]):
    soup = bs4.BeautifulSoup(html, "lxml")
    root = next(soup.html.body.children)

    with pytest.raises(exception):
        get_approx_table_metrics(root)
