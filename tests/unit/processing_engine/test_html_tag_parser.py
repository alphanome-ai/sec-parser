import pytest

from sec_parser.processing_engine import HtmlTagParser

from sec_parser.exceptions import SecParserValueError


@pytest.mark.parametrize(
    "html_string",
    [
        "",
        "<html></html>",
        "<html><body></body></html>",
    ],
)
def test_parse_no_html(html_string):
    # Arrange
    parser = HtmlTagParser()

    # Act and Assert
    with pytest.raises(SecParserValueError):
        parser.parse(html_string)
