from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from sec_parser.exceptions import SecParserValueError
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)
from sec_parser.utils.py_utils import exceeds_capitalization_threshold

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag
    from sec_parser.processing_engine.processing_log import LogItemOrigin, ProcessingLog


class HighlightedTextElement(AbstractSemanticElement):
    """
    The HighlightedTextElement class, among other uses,
    is an intermediate step in identifying title elements.

    For example:
    ============
    First, elements with specific styles (like bold or italic text)
    are classified as HighlightedTextElements.
    These are later examined to determine if they should
    be considered TitleElements.
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        *,
        processing_log: ProcessingLog | None = None,
        style: TextStyle | None = None,
        log_origin: LogItemOrigin | None = None,
    ) -> None:
        super().__init__(html_tag, processing_log=processing_log, log_origin=log_origin)
        if style is None:
            msg = "styles must be specified for HighlightedElement"
            raise SecParserValueError(msg)
        self.style = style

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        log_origin: LogItemOrigin,
        *,
        style: TextStyle | None = None,
    ) -> HighlightedTextElement:
        if style is None:
            msg = "Style must be provided."
            raise SecParserValueError(msg)
        return cls(
            source.html_tag,
            style=style,
            processing_log=source.processing_log,
            log_origin=log_origin,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "text_style": asdict(self.style),
        }


@dataclass(frozen=True)
class TextStyle:
    PERCENTAGE_THRESHOLD = 80
    BOLD_THRESHOLD = 600

    is_all_uppercase: bool = False
    bold_with_font_weight: bool = False
    italic: bool = False
    centered: bool = False
    underline: bool = False

    def __bool__(self) -> bool:
        return any(asdict(self).values())

    @classmethod
    def from_style_and_text(
        cls,
        style_percentage: dict[tuple[str, str], float],
        text: str,
    ) -> TextStyle:
        # Text checks
        is_all_uppercase = exceeds_capitalization_threshold(
            text,
            cls.PERCENTAGE_THRESHOLD,
        )

        # Filter styles that meet the percentage threshold
        filtered_styles = {
            (k, v): p
            for (k, v), p in style_percentage.items()
            if p >= cls.PERCENTAGE_THRESHOLD
        }

        # Define checks for each style
        style_checks = {
            "bold_with_font_weight": cls._is_bold_with_font_weight,
            "italic": lambda k, v: k == "font-style" and v == "italic",
            "centered": lambda k, v: k == "text-align" and v == "center",
            "underline": lambda k, v: k == "text-decoration" and v == "underline",
        }

        # Apply checks to the filtered styles
        style_results = {
            style: any(check(k, v) for (k, v) in filtered_styles)
            for style, check in style_checks.items()
        }

        # Return a TextStyle instance with the results
        return cls(
            is_all_uppercase=is_all_uppercase,
            bold_with_font_weight=style_results["bold_with_font_weight"],
            italic=style_results["italic"],
            centered=style_results["centered"],
            underline=style_results["underline"],
        )

    @classmethod
    def _is_bold_with_font_weight(cls, key: str, value: str) -> bool:
        if key != "font-weight":
            return False
        if value == "bold":
            return True
        try:
            return int(value) >= cls.BOLD_THRESHOLD
        except ValueError:
            return False
