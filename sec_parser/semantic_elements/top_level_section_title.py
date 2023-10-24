from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag


class TopLevelSectionTitle(AbstractLevelElement):
    """
    The TopLevelSectionTitle class represents the title and the beginning of a top-level
    section of a document. For instance, in SEC 10-Q reports, a
    top-level section could be "Part I, Item 3. Quantitative and Qualitative
    Disclosures About Market Risk.".
    """

    def __init__(
        self,
        html_tag: HtmlTag,
        transformation_history: tuple[AbstractSemanticElement, ...],
        level: int | None = None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(html_tag, transformation_history, level)
        self.identifier = identifier

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        *,
        level: int | None = None,
        identifier: str | None = None,
    ) -> AbstractLevelElement:
        return cls(
            source._html_tag,  # noqa: SLF001
            source.get_transformation_history(),
            level=level,
            identifier=identifier,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "identifier": self.identifier,
        }
