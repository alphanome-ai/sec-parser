from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    AlreadyTransformedError,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.highlighted_element import (
    HighlightedElement,
    TextStyles,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )

from sec_parser.semantic_elements.convert_from import convert_from


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
            return convert_from(element, to=HighlightedElement, styles=styles)
        return element

    def _transform_to_title_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        return element
