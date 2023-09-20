from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag

class HighlightedElement(AbstractSemanticElement):
    """
    The HighlightedElement class used for detecting title elements.
    The process begins with the detection of highlighted elements,
    which are then further classified into title elements.
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        *,
        inner_elements: list[AbstractSemanticElement] | None = None,
        styles: TextStyles | None = None,
    ) -> None:
        super().__init__(html_tag, inner_elements=inner_elements)
        if styles is None:
            msg = "styles must be specified for HighlightedElement"
            raise ValueError(msg)
        self._styles: TextStyles = styles

    @classmethod
    def convert_from(
        cls,
        source: AbstractSemanticElement,
        *,
        styles: TextStyles| None = None,
    ) -> HighlightedElement:
        return cls(
            source.html_tag,
            inner_elements=source.inner_elements,
            styles=styles,
        )


@dataclass(frozen=True)
class TextStyles:
    PERCENTAGE_THRESHOLD = 80
    BOLD_THRESHOLD = 600

    bold_with_font_weight: bool
    # italic?
    # underline?
    # all-caps?

    @classmethod
    def from_style_string(
        cls,
        style_string: dict[tuple[str, str], float],
    ) -> TextStyles:
        bold_with_font_weight = False
        for (key, value), percentage in style_string.items():
            if percentage < cls.PERCENTAGE_THRESHOLD:
                continue
            bold_with_font_weight |= cls._is_bold_with_font_weight(key, value)
        return cls(bold_with_font_weight=bold_with_font_weight)

    @classmethod
    def _is_bold_with_font_weight(cls, key: str, value: str) -> bool:
        if key != "font-weight":
            return False
        if value == "bold":
            return True
        try:
            font_weight = int(value)
        except ValueError:
            return False
        return font_weight >= cls.BOLD_THRESHOLD
