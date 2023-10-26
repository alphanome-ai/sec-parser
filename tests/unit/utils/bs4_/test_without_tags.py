import bs4
from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.without_tags import without_tags


def test_without_tags_single_tag():
    # Arrange
    html = "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = without_tags(tag, ["b"])

    # Assert
    assert (
        str(result) == "<div><p>bar<i>bax</i></p></div>"
    ), "Expected 'b' tags to be removed"


def test_without_tags_multiple_tags():
    # Arrange
    html = "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = without_tags(tag, ["b", "i"])

    # Assert
    assert (
        str(result) == "<div><p>bar</p></div>"
    ), "Expected 'b' and 'i' tags to be removed"


def test_without_tags_nonexistent_tag():
    # Arrange
    html = "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = without_tags(tag, ["a"])

    # Assert
    assert (
        str(result) == "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    ), "Expected no changes when tag does not exist"


def test_without_tags_empty_input():
    # Arrange
    html = "<div></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = without_tags(tag, ["p"])

    # Assert
    assert str(result) == "<div></div>", "Expected no changes when tag is empty"


def test_without_tags_empty_tag_list():
    # Arrange
    html = "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = without_tags(tag, [])

    # Assert
    assert (
        str(result) == "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    ), "Expected no changes when tag list is empty"

    # Assert
    assert (
        str(result) == "<div><b>foo</b><p>bar<i>bax</i></p></div>"
    ), "Expected no changes when tag list is empty"
