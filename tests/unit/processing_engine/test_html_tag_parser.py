import pytest

from sec_parser.processing_engine import HtmlTagParser


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
    with pytest.raises(ValueError):
        parser.parse(html_string)
