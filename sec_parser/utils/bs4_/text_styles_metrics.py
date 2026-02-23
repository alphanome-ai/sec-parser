from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from sec_parser.exceptions import SecParserValueError

if TYPE_CHECKING:  # pragma: no cover
    from bs4 import Tag

# HTML semantic tags that imply CSS styles, even without an explicit style attribute.
# This allows the classifier to detect bold/italic/underline applied via <b>, <strong>,
# <i>, <em>, and <u> tags in addition to inline CSS (e.g. font-weight: bold).
_SEMANTIC_TAG_STYLES: dict[str, dict[str, str]] = {
    "b": {"font-weight": "bold"},
    "strong": {"font-weight": "bold"},
    "i": {"font-style": "italic"},
    "em": {"font-style": "italic"},
    "u": {"text-decoration": "underline"},
}


def compute_text_styles_metrics(tag: Tag) -> dict[tuple[str, str], float]:
    """
    Compute the percentage distribution of various CSS styles within the
    text content of a given HTML tag and its descendants.

    This function iterates through all the text nodes within the tag,
    recursively includes text from child elements, and calculates the
    effective styles applied to each text segment.

    It aggregates these styles and computes their percentage distribution
    based on the length of text they apply to.

    The function uses BeautifulSoup's recursive text search and parent
    traversal features. It returns a dictionary containing the aggregated
    style metrics (the percentage distribution of styles).

    Each dictionary entry corresponds to a unique style, (property, value)
    and the percentage of text it affects.
    """
    total_chars: int = 0
    style_metrics: dict[tuple[str, str], float] = defaultdict(float)

    for text_node in tag.find_all(string=True, recursive=True):
        text: str = text_node.strip()
        char_count: int = len(text)
        if char_count == 0:
            continue

        total_chars += char_count
        parent = text_node.find_parent()

        effective_styles: dict[str, str] = _compute_effective_style(parent)

        for prop, val in effective_styles.items():
            style_metrics[(prop, val)] += char_count

    for key in style_metrics:
        style_metrics[key] = (
            (style_metrics[key] / total_chars) * 100 if total_chars else 0
        )

    return style_metrics


def _compute_effective_style(tag: Tag) -> dict[str, str]:
    """
    Aggregate the effective styles for a given tag by
    traversing up the parent hierarchy.

    In addition to inline ``style`` attributes, this function also recognises
    semantic HTML tags (``<b>``, ``<strong>``, ``<i>``, ``<em>``, ``<u>``)
    whose names imply specific CSS properties.  This ensures that text
    emphasised via bare ``<b>`` or ``<strong>`` tags (rather than via
    ``style="font-weight:bold"``) is correctly detected as highlighted.
    """
    effective_styles: dict[str, str] = {}
    found_tag: Tag | None = tag
    while found_tag:
        # Inline style attributes take precedence over semantic tag names, so
        # process them first (setdefault ensures the innermost/highest-specificity
        # rule wins as we traverse toward the root).
        if "style" in found_tag.attrs:
            found_styles = found_tag["style"]
            if isinstance(found_styles, list):  # pragma: no cover
                # this should never happen, can't even construct a
                # scenario where this would occur
                msg = "Expected a string, got a list"
                raise SecParserValueError(msg)
            styles = found_styles.split(";")
            for style in styles:
                if ":" in style:
                    prop, val = style.split(":", 1)
                    prop = prop.strip()
                    val = val.strip()
                    # Only set if not previously set to respect CSS cascading rules
                    effective_styles.setdefault(prop, val)

        # After inline styles, check for implied styles from semantic HTML tag
        # names (e.g. <b>, <strong>, <i>, <em>, <u>).  setdefault ensures an
        # explicit inline style on the same element still wins.
        tag_name = getattr(found_tag, "name", None)
        if tag_name and tag_name in _SEMANTIC_TAG_STYLES:
            for prop, val in _SEMANTIC_TAG_STYLES[tag_name].items():
                effective_styles.setdefault(prop, val)

        found_tag = found_tag.find_parent()
    return effective_styles
