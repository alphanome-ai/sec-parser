import bs4
import pytest

from sec_parser.utils.bs4_.get_single_table import (
    MultipleTablesFoundError,
    NoTableFoundError,
    get_single_table,
)


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
        get_single_table(root)
