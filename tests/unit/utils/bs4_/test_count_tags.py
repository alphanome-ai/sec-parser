from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.count_tags import count_tags


def test_count_tags_with_self_included():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = count_tags(tag, "div")

    # Assert
    assert result == 1, "Expected 1 when tag is included in count"


def test_count_tags_with_descendant_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div

    # Act
    result = count_tags(tag, "b")

    # Assert
    assert result == 1, "Expected 1 when descendant tag is present"


def test_count_tags_without_descendant_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = count_tags(tag, "a")

    # Assert
    assert result == 0, "Expected 0 when descendant tag is not present"


def test_count_tags_with_empty_tag():
    # Arrange
    html = "<div></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = count_tags(tag, "p")

    # Assert
    assert result == 0, "Expected 0 when tag is empty"


def test_count_tags_with_nonexistent_tag():
    # Arrange
    html = "<div><p><b>text</b></p></div>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.div
    assert tag

    # Act
    result = count_tags(tag, "nonexistent")

    # Assert
    assert result == 0, "Expected 0 when tag does not exist"


def test_count_tags_with_root_tag():
    # Arrange
    html = "<b>text</b>"
    soup = BeautifulSoup(html, "lxml")
    tag = soup.b
    assert tag

    # Act
    result = count_tags(tag, "b")

    # Assert
    assert result == 1, "Expected 1 when tag is at the root"
