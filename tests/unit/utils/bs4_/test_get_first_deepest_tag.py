from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.get_first_deepest_tag import get_first_deepest_tag


def test_get_first_deepest_tag():
    # Arrange
    html = "<html><body><div><p>Test</p><span>Another Test</span></div></body></html>"
    soup = BeautifulSoup(html, "lxml")

    # Act
    deepest_tag = get_first_deepest_tag(soup.html)

    # Assert
    assert deepest_tag.name == "p"


def test_get_first_deepest_tag_no_children():
    # Arrange
    html = "<p>Test</p>"
    soup = BeautifulSoup(html, "lxml")

    # Act
    deepest_tag = get_first_deepest_tag(soup.p)

    # Assert
    assert deepest_tag.name == "p"


def test_get_first_deepest_tag_empty():
    # Arrange
    html = "<p></p>"
    soup = BeautifulSoup(html, "lxml")

    # Act
    deepest_tag = get_first_deepest_tag(soup.p)

    # Assert
    assert deepest_tag.name == "p"


def test_get_first_deepest_tag_with_whitespace():
    # Arrange
    html = "<div>   <p>Test</p><span>Another Test</span></div>"
    soup = BeautifulSoup(html, "lxml")

    # Act
    deepest_tag = get_first_deepest_tag(soup.div)

    # Assert
    assert deepest_tag.name == "p"
