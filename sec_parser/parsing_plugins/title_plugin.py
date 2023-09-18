from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    AlreadyTransformedError,
    ElementwiseParsingContext,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TitlePlugin(AbstractElementwiseParsingPlugin):
    """
    TitlePlugin class for transforming elements into TitleElement instances.

    This plugin scans through a list of semantic elements and replaces
    suitable candidates with TitleElement instances.
    """

    iteration_count = 2

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        context: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        if context.current_iteration >= self.iteration_count:
            msg = (
                "This Plugin instance has already processed a document. "
                "Each plugin instance is designed for a single "
                "transformation operation. Please create a new "
                "instance of the Plugin to process another document."
            )
            raise AlreadyTransformedError(msg)

        if context.current_iteration == 0:
            return self._transform_to_highlighted_element(element, context)
        return self._transform_to_title_element(element, context)

    def _transform_to_highlighted_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        return element

    def _transform_to_title_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        return element
