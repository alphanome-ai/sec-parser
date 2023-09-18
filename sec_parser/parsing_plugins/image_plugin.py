from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class ImagePlugin(AbstractElementwiseParsingPlugin):
    """
    ImagePlugin class for transforming elements into ImageElement instances.

    This plugin scans through a list of semantic elements and replaces
    suitable candidates with ImageElement instances.
    """

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        return element
