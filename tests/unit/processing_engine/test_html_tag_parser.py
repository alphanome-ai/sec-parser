import pytest

from sec_parser.exceptions import SecParserValueError
from sec_parser.processing_engine import HtmlTagParser


@pytest.mark.parametrize(
    "html_string",
    [
        "",
        "<html></html>",
        "<html><body></body></html>",
    ],
)
def test_parse_no_html(html_string) -> None:
    # Arrange
    parser = HtmlTagParser()

    # Act and Assert
    with pytest.raises(SecParserValueError):
        parser.parse(html_string)
