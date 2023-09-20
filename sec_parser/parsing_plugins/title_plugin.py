from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    AlreadyTransformedError,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractSemanticElement,
)

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag



class TitlePlugin(AbstractElementwiseParsingPlugin):
    """
    TitlePlugin class for transforming elements into TitleElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TitleElement instances.
    """

    iteration_count = 2

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        if context.current_iteration == 0:
            return self._transform_to_highlighted_element(element, context)
        if context.current_iteration == 1:
            return self._transform_to_title_element(element, context)

        msg = (
            "This Plugin instance has already processed a document. "
            "Each plugin instance is designed for a single "
            "transformation operation. Please create a new "
            "instance of t`he Plugin to process another document."
        )
        raise AlreadyTransformedError(msg)

    def _transform_to_highlighted_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        styles_metrics = element.html_tag.get_text_styles_metrics()
        styles: TextStyles = TextStyles.from_style_string(styles_metrics)
        if styles.bold_with_font_weight:
            return HighlightedElement.convert_from(element, styles=styles)
        return element

    def _transform_to_title_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        return element


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


class HighlightedElement(AbstractSemanticElement):
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
        styles: TextStyles | None = None,
    ) -> None:
        super().__init__(html_tag, inner_elements)
        if styles is None:
            msg = "styles must be specified for HighlightedElement"
            raise ValueError(msg)
        self._styles = styles

    @classmethod
    def convert_from(
        cls,
        source: AbstractSemanticElement,
        *,
        styles: TextStyles| None = None,
    ) -> HighlightedElement:
        return cls(
            source.html_tag,
            source.inner_elements,
            styles=styles,
        )
