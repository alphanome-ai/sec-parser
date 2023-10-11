from sec_parser.processing_engine import HtmlTagParser


def test_parse_no_body():
    # Arrange
    parser = HtmlTagParser()
    html_string = "<html></html>"

    # Act
    result = parser.parse(html_string)

    # Assert
    assert result == []
