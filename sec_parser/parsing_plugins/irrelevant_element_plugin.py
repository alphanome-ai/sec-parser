from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin

if TYPE_CHECKING:
    from sec_parser.semantic_elements.base_semantic_element import (
        BaseSemanticElement,
    )


class IrrelevantElementPlugin(AbstractParsingPlugin):
    """
    IrrelevantElementPlugin class for transforming elements into
    IrrelevantElement instances.

    This plugin scans through a list of semantic elements and
    replaces suitable candidates with IrrelevantElement instances.
    """

    def transform(
        self,
        elements: list[BaseSemanticElement],
    ) -> list[BaseSemanticElement]:
        return elements
