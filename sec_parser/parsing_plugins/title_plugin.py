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
from sec_parser.semantic_elements.semantic_elements import TitleElement

if TYPE_CHECKING:
    from sec_parser.parsing_engine.html_parsers.html_tag import HtmlTag



class TitlePlugin(AbstractElementwiseParsingPlugin):
    """
    TitlePlugin class for transforming elements into TitleElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TitleElement instances.
    """

    iteration_count = 2

    def __init__(
        self,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            process_only=process_only,
            except_dont_process=except_dont_process,
        )

        # _styles track unique styles in the document.
        # Stored in a tuple as an ordered set, preserving insertion order.
        # This order is used to determine a style's level.
        # It is based on the observation that "highlight" styles that appear first
        # typically mark higher level paragraph/section headings.
        # _styles is effectively used as an ordered set:
        self._styles: tuple[str, ...] = ()

    def _found_style(self, symbol: str) -> None:
        if symbol not in self._styles:
            # _styles is effectively updated as an ordered set:
            self._styles = tuple(
                dict.fromkeys([*self._styles, symbol]).keys(),
            )

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
            "instance of the Plugin to process another document."
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
            return TitleElement.convert_from(element, level=1)
            return HighlightedElement.convert_from(element, styles=styles)
        return element

    def _transform_to_title_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        import streamlit as st
        if isinstance(element, HighlightedElement):
            st.write("A")
            st.stop()
        return element


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
        styles: TextStyles | None = None,
    ) -> HighlightedElement:
        return cls(
            source.html_tag,
            source.inner_elements,
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

