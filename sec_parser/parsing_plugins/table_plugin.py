from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_elementwise_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.semantic_elements import TableElement

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class TablePlugin(AbstractElementwiseParsingPlugin):
    """
    TablePlugin class for transforming elements into TableElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with TableElement instances.
    """

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        is_unary = element.html_tag.is_unary_tree()
        contains_table = element.html_tag.contains_tag("table", include_self=True)
        if is_unary and contains_table:
            return TableElement.convert_from(element)

        return element
