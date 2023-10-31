import pytest
from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.has_text_outside_tags import has_text_outside_tags


# Normal case with text outside tag
@pytest.mark.parametrize(
    ("html", "expected"),
    [
        # Simple cases
        ("", False),
        ("<p></p>", False),
        ("<p>Hello, World!</p>", True),
        ("<div><span>Hi!</span></div>", True),
        ("<table><tr><td>Data</td></tr></table>", False),
        # Advanced cases
        (
            """<div>
                <span>Hi!</span>
                <p>Text outside</p>
            </div>""",
            True,
        ),
        (
            """<table><tr><td>Data</td></tr></table>
            Text outside""",
            True,
        ),
        (
            """<table><tr><td>Data</td></tr></table>
            <p>Text outside</p>""",
            True,
        ),
        (
            """<div>
                <table><tr><td>Data</td></tr></table>
                Text outside
            </div>""",
            True,
        ),
        (
            """<div>
                <table><tr><td>Data</td></tr></table>
                <p>Text outside</p>
            </div>""",
            True,
        ),
    ],
)
def test_has_text_outside_tag_normal_cases(html, expected):
    # Arrange
    soup = BeautifulSoup(html, "lxml")

    # Act
    result = has_text_outside_tags(soup, ("table",))

    # Assert
    assert result == expected
