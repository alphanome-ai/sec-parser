from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import (
    EmptyElement,
    TextElement,
    UndeterminedElement,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TextPlugin(AbstractElementwiseParsingPlugin):
    """
    TextPlugin class for transforming elements into TextElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TextElement instances.
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
        if not isinstance(element, UndeterminedElement):
            return element

        if element.html_tag.get_text() == "":
            return EmptyElement.convert_from(element)
        return TextElement.convert_from(element)
