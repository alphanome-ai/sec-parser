from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import TextElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.base_semantic_element import (
        BaseSemanticElement,
    )


class TextPlugin(AbstractElementwiseParsingPlugin):
    """
    TextPlugin class for transforming elements into TextElement instances.

    This plugin scans through a list of semantic elements and replaces
    suitable candidates with TextElement instances.
    """

    def __init__(
        self,
        dont_convert_from: set[type[BaseSemanticElement]] | None = None,
    ) -> None:
        self._ignored_types = dont_convert_from or set()

    def transform_element(
        self,
        element: BaseSemanticElement,
        _: ElementwiseParsingContext,
    ) -> BaseSemanticElement:
        """
        Transform a single semantic element
        into a TextElement if applicable.
        """
        for ignored_type in self._ignored_types:
            if isinstance(element, ignored_type):
                return element
        if element.html_tag.text.strip() == "":
            return element
        return TextElement.convert_from(element)
