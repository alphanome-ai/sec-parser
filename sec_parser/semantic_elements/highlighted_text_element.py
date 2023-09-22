from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag


class HighlightedTextElement(AbstractSemanticElement):
    """
    The HighlightedElement class used for detecting title elements.
    The process begins with the detection of highlighted elements,
    which are then further classified into title elements.
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        inner_elements: list[AbstractSemanticElement],
        *,
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(html_tag, inner_elements)
        if style is None:
            msg = "styles must be specified for HighlightedElement"
            raise ValueError(msg)
        self.style = style

    @classmethod
    def convert_from(
        cls,
        source: AbstractSemanticElement,
        *,
        style: TextStyle | None = None,
    ) -> HighlightedTextElement:
        return cls(
            source.html_tag,
            source.inner_elements,
            style=style,
        )


@dataclass(frozen=True)
class TextStyle:
    PERCENTAGE_THRESHOLD = 80
    BOLD_THRESHOLD = 600

    bold_with_font_weight: bool
    italic: bool
    # underline?
    # all-caps?

    def __bool__(self) -> bool:
        return any(asdict(self).values())

    @classmethod
    def from_style_string(
        cls,
        style_string: dict[tuple[str, str], float],
    ) -> TextStyle:
        filtered_styles = {
            (k, v): p for (k, v), p in style_string.items()
            if p >= cls.PERCENTAGE_THRESHOLD
        }

        bold_with_font_weight = any(
            cls._is_bold_with_font_weight(k, v)
            for (k, v) in filtered_styles
        )

        italic = any(
            k == "font-style" and v == "italic"
            for (k, v) in filtered_styles
        )

        return cls(
            bold_with_font_weight=bold_with_font_weight,
            italic=italic,
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
