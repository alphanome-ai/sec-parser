from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import IrrelevantElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class IrrelevantElementPlugin(AbstractElementwiseParsingPlugin):
    """
    IrrelevantElementPlugin class for transforming elements into
    IrrelevantElement instances.

    This plugin scans through a list of semantic elements and
    replaces suitable candidates with IrrelevantElement instances.
    """

    def transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        if element.html_tag.text.strip() == "":
            return IrrelevantElement.convert_from(element)

        return element
