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


def test_should_detect_bold_from_b_tag():
    """Text wrapped in <b> should be detected as font-weight:bold."""
    # Arrange
    html = "<p><b>Bold text</b></p>"
    soup = BeautifulSoup(html, "lxml")
    p_tag = soup.find("p")

    # Act
    result = compute_text_styles_metrics(p_tag)

    # Assert
    assert result[("font-weight", "bold")] == 100.0


def test_should_detect_bold_from_strong_tag():
    """Text wrapped in <strong> should be detected as font-weight:bold."""
    # Arrange
    html = "<p><strong>Bold text</strong></p>"
    soup = BeautifulSoup(html, "lxml")
    p_tag = soup.find("p")

    # Act
    result = compute_text_styles_metrics(p_tag)

    # Assert
    assert result[("font-weight", "bold")] == 100.0


def test_should_detect_italic_from_i_tag():
    """Text wrapped in <i> should be detected as font-style:italic."""
    # Arrange
    html = "<p><i>Italic text</i></p>"
    soup = BeautifulSoup(html, "lxml")
    p_tag = soup.find("p")

    # Act
    result = compute_text_styles_metrics(p_tag)

    # Assert
    assert result[("font-style", "italic")] == 100.0


def test_should_detect_italic_from_em_tag():
    """Text wrapped in <em> should be detected as font-style:italic."""
    # Arrange
    html = "<p><em>Italic text</em></p>"
    soup = BeautifulSoup(html, "lxml")
    p_tag = soup.find("p")

    # Act
    result = compute_text_styles_metrics(p_tag)

    # Assert
    assert result[("font-style", "italic")] == 100.0


def test_inline_style_should_override_semantic_tag():
    """Explicit inline style takes precedence over implied style from tag name."""
    # Arrange - <b> implies bold, but inline style overrides with 400 (normal weight)
    html = '<p><b style="font-weight:400">Not actually bold</b></p>'
    soup = BeautifulSoup(html, "lxml")
    p_tag = soup.find("p")

    # Act
    result = compute_text_styles_metrics(p_tag)

    # Assert — the inline style (400) wins because it is processed before the
    # semantic tag name, so setdefault skips the "bold" implied value.
    assert result[("font-weight", "400")] == 100.0
    assert ("font-weight", "bold") not in result
