from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import TextElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TextPlugin(AbstractElementwiseParsingPlugin):
    """
    TextPlugin class for transforming elements into TextElement instances.

    This plugin scans through a list of semantic elements and replaces
    suitable candidates with TextElement instances.
    """

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        """
        Transform a single semantic element
        into a TextElement if applicable.
        """
        if element.html_tag.text == "":
            return element
        return TextElement.convert_from(element)
