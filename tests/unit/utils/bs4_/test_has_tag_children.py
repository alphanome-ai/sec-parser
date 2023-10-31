# Normal case with text outside tag
import bs4
import pytest

from sec_parser.utils.bs4_.has_tag_children import has_tag_children


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<p></p>", False),
        ("<p><b>Hello, World!</b></p>", True),
    ],
)
def test_has_tag_children(html, expected):
    # Arrange
    p = bs4.BeautifulSoup(html, "lxml").p
    assert isinstance(p, bs4.Tag)

    # Act
    result = has_tag_children(p)

    # Assert
    assert result == expected
