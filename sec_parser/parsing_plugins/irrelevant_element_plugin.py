from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class IrrelevantElementPlugin(AbstractParsingPlugin):
    def transform(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        IrrelevantElementPlugin replace matching elements with
        IrrelevantElement class instances.
        """
        return elements
