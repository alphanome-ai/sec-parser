from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.processing_steps.abstract_classes.abstract_elementwise_processing_step import (
    AbstractElementwiseProcessingStep,
    ElementProcessingContext,
)
from sec_parser.semantic_elements.highlighted_text_element import (
    HighlightedTextElement,
    TextStyle,
)
from sec_parser.semantic_elements.title_element import TitleElement

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TitleClassifier(AbstractElementwiseProcessingStep):
    """
    TitleClassifier elements into TitleElement instances by scanning a list
    of semantic elements and replacing suitable candidates.

    The "_unique_styles_by_order" tuple:
    ====================================
    - Represents an ordered set of unique styles found in the document.
    - Preserves the order of insertion, which determines the hierarchical
      level of each style.
    - Assumes that earlier "highlight" styles correspond to higher level paragraph
      or section headings.
    """

    def __init__(
        self,
        types_to_process: set[type[AbstractSemanticElement]] | None = None,
        types_to_exclude: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            types_to_process=types_to_process,
            types_to_exclude=types_to_exclude,
        )

        self._unique_styles_by_order: tuple[TextStyle, ...] = ()

    def _add_unique_style(self, style: TextStyle) -> None:
        """Add a new unique style if not already present."""
        if style not in self._unique_styles_by_order:
            self._unique_styles_by_order = tuple(
                dict.fromkeys([*self._unique_styles_by_order, style]).keys(),
            )

    def _process_element(
        self,
        element: AbstractSemanticElement,
        _: ElementProcessingContext,
    ) -> AbstractSemanticElement:
        """Process each element and convert to TitleElement if necessary."""
        if not isinstance(element, HighlightedTextElement):
            return element

        # Ensure the style is tracked
        self._add_unique_style(element.style)

        level = self._unique_styles_by_order.index(element.style)
        return TitleElement.create_from_element(
            element,
            level=level,
            log_origin=self.__class__.__name__,
        )
