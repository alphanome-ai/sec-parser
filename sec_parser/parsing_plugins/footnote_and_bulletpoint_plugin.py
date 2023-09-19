from __future__ import annotations

from typing import TYPE_CHECKING

from sec_parser.parsing_plugins.abstract_parsing_plugin import (
    AbstractElementwiseParsingPlugin,
    ElementwiseParsingContext,
)
from sec_parser.semantic_elements.convert_from import convert_from
from sec_parser.semantic_elements.semantic_elements import (
    BulletpointTextElement,
    FootnoteTextElement,
)

if TYPE_CHECKING:
    from sec_parser.semantic_elements.abstract_semantic_element import (
        AbstractSemanticElement,
    )


class FootnoteAndBulletpointPlugin(AbstractElementwiseParsingPlugin):
    """
    FootnoteAndBulletpointPlugin class for transforming elements into
    BulletpointTextElement and FootnoteTextElement instances.

    This plugin scans through a list of semantic elements and changes it,
    primarily by replacing suitable candidates with
    BulletpointElement and FootnoteTextElement instances.
    """

    def __init__(
        self,
        *,
        process_only: set[type[AbstractSemanticElement]] | None = None,
        except_dont_process: set[type[AbstractSemanticElement]] | None = None,
    ) -> None:
        super().__init__(
            process_only=process_only,
            except_dont_process=except_dont_process,
        )
        self._marker_symbols: tuple[str, ...] = ()

    def _found_marker(self, symbol: str) -> None:
        if symbol not in self._marker_symbols:
            # Ordered set:
            self._marker_symbols = tuple(
                dict.fromkeys([*self._marker_symbols, symbol]).keys(),
            )

    def _transform_element(
        self,
        element: AbstractSemanticElement,
        _: ElementwiseParsingContext,
    ) -> AbstractSemanticElement:
        deepest_tag = element.html_tag.get_first_deepest_tag()
        if not deepest_tag:
            return element

        marker = deepest_tag.get_text()
        if not marker:
            return element

        if marker.replace(".", "").isdigit():
            return FootnoteTextElement.convert_from(element)

        if len(marker) == 1:
            self._found_marker(marker)
            level = 1 + self._marker_symbols.index(marker)
            return convert_from(element, to=BulletpointTextElement, level=level)

        return element
