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
from sec_parser.semantic_elements.semantic_elements import TitleElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TitlePlugin(AbstractElementwiseParsingPlugin):
    """
    TitlePlugin class for transforming elements into TitleElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TitleElement instances.
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

        # _unique_styles_by_order track unique styles in the document.
        # Stored in a tuple as an ordered set, preserving insertion order.
        # This order is used to determine a style's level.
        # It is based on the observation that "highlight" styles that appear first
        # typically mark higher level paragraph/section headings.
        # _unique_styles_by_order is effectively used as an ordered set:
        self._unique_styles_by_order: tuple[TextStyle, ...] = ()

    def _add_unique_style(self, style: TextStyle) -> None:
        if style not in self._unique_styles_by_order:
            # _styles is effectively updated as an ordered set:
            self._unique_styles_by_order = tuple(
                dict.fromkeys([*self._unique_styles_by_order, style]).keys(),
            )

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        if not isinstance(element, HighlightedTextElement):
            return element
        self._add_unique_style(element.style)
        level = self._unique_styles_by_order.index(element.style)
        return TitleElement.convert_from(element, level=level)
