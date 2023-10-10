from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.is_unary_tree import is_unary_tree


def test_is_unary_tree_with_only_tags():
    # Arrange
    html = """
    <div>
      <p>
        <span></span>
      </p>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert result is True, "Expected a unary tree with only tags to return True"


def test_is_unary_tree_with_leaf_text():
    # Arrange
    html = """
    <div>
      <p>
        <span>Text</span>
      </p>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert (
        result is True
    ), "Expected a unary tree with non-empty leaf NavigableString to return True"


def test_is_not_unary_tree():
    # Arrange
    html = """
    <div>
      <p></p>
      <p></p>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert result is False, "Expected a non-unary tree to return False"


def test_is_unary_tree_with_non_leaf_text_before():
    # Arrange
    html = """
    <div>
      <p>Text
        <span></span>
      </p>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert (
        result is False
    ), "Expected a unary tree with non-empty NavigableString at a non-leaf node to return False"


def test_is_unary_tree_with_non_leaf_text_after():
    # Arrange
    html = """
    <div>
      <p>
        <span></span>
      </p>Text
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert (
        result is False
    ), "Expected a unary tree with non-empty NavigableString at a non-leaf node to return False"


def test_is_unary_tree_with_empty_tag():
    # Arrange
    html = "<div></div>"
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert result is True, "Expected a tag with no children to return True"


def test_is_unary_tree_with_table_as_child():
    # Arrange
    html = """
    <div>
      <table>
        <tr>
          <td>Data</td>
        </tr>
      </table>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert (
        result is True
    ), "Expected a unary tree with a table as a child to return True"


def test_is_unary_tree_with_table_as_root():
    # Arrange
    html = """
    <table>
      <tr>
        <td>Data</td>
      </tr>
    </table>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("table")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert result is True, "Expected a table as root to return True"


def test_is_not_unary_tree_with_multiple_tables():
    # Arrange
    html = """
    <div>
      <table>
        <tr>
          <td>Data</td>
        </tr>
      </table>
      <table>
        <tr>
          <td>Data</td>
        </tr>
      </table>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div")

    # Act
    result = is_unary_tree(root)

    # Assert
    assert result is False, "Expected a tree with multiple tables to return False"
