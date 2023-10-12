import pytest
from bs4 import BeautifulSoup

from sec_parser.utils.bs4_.text_styles_metrics import compute_text_styles_metrics


# Test: Normal case with multiple styles
def test_should_return_correct_metrics_for_multiple_styles():
    # Arrange
    html = """
    <div>
        <span style="color:#000000;">This is text</span>
        <span style="font-weight:600;">This is bold</span>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    div_tag = soup.find("div")

    # Act
    result = compute_text_styles_metrics(div_tag)

    # Assert
    assert result[("color", "#000000")] == 50.0
    assert result[("font-weight", "600")] == 50.0


# Test: Edge case with no text
def test_should_return_empty_metrics_for_no_text():
    # Arrange
    html = "<div></div>"
    soup = BeautifulSoup(html, "lxml")
    div_tag = soup.find("div")

    # Act
    result = compute_text_styles_metrics(div_tag)

    # Assert
    assert result == {}


def test_should_return_correct_metrics_for_inherited_styles():
    # Arrange
    html = """
    <div style="color:#000000;">
        <span>This is text</span>
        <span style="font-weight:600;">This is bold</span>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")
    div_tag = soup.find("div")

    # Act
    result = compute_text_styles_metrics(div_tag)

    # Assert
    assert result[("color", "#000000")] == 100.0
    assert result[("font-weight", "600")] == 50.0
