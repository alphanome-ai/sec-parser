from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_elementwise_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.highlighted_text_element import (
    HighlightedTextElement,
    TextStyle,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class HighlightedTextPlugin(AbstractElementwiseParsingPlugin):
    """
    HighlightedText class for transforming elements into HighlightedText instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with HighlightedText instances.
    """

    def __init__(
        self,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            process_only=process_only,
            except_dont_process=except_dont_process,
        )

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        styles_metrics = element.html_tag.get_text_styles_metrics()
        style: TextStyle = TextStyle.from_style_string(styles_metrics)
        if not style:
            return element
        return HighlightedTextElement.convert_from(element, style=style)
