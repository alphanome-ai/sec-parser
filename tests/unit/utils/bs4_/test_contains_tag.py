from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.contains_tag import contains_tag


def test_contains_tag_with_self_included():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Acts
    result = contains_tag(tag, "div", include_self=True)

    # Assert
    assert result is True, "Expected True when tag is included in search"


def test_contains_tag_with_self_excluded():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = contains_tag(tag, "div", include_self=False)

    # Assert
    assert result is False, "Expected False when tag is excluded from search"


def test_contains_tag_with_descendant_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div

    # Act
    result = contains_tag(tag, "b")

    # Assert
    assert result is True, "Expected True when descendant tag is present"


def test_contains_tag_without_descendant_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = contains_tag(tag, "a")

    # Assert
    assert result is False, "Expected False when descendant tag is not present"


def test_contains_tag_with_empty_tag():
    # Arrange
    html = "<div></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = contains_tag(tag, "p")

    # Assert
    assert result is False, "Expected False when tag is empty"


def test_contains_tag_with_nonexistent_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div

    # Act
    result = contains_tag(tag, "nonexistent")

    # Assert
    assert result is False, "Expected False when tag does not exist"
