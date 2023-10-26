from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sec_parser.semantic_elements.abstract_semantic_element import (
    AbstractLevelElement,
    AbstractSemanticElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from sec_parser.processing_engine.html_tag import HtmlTag
    from sec_parser.processing_engine.processing_log import LogItemOrigin, ProcessingLog


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
        *,
        processing_log: ProcessingLog | None = None,
        log_origin: LogItemOrigin | None = None,
        level: int | None = None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(
            html_tag,
            processing_log=processing_log,
            level=level,
            log_origin=log_origin,
        )
        self.identifier = identifier

    @classmethod
    def create_from_element(
        cls,
        source: AbstractSemanticElement,
        log_origin: LogItemOrigin,
        *,
        level: int | None = None,
        identifier: str | None = None,
    ) -> AbstractLevelElement:
        return cls(
            source._html_tag,  # noqa: SLF001
            level=level,
            identifier=identifier,
            processing_log=source.processing_log,
            log_origin=log_origin,
        )

    def to_dict(self, include_html_tag: bool | None = None) -> dict[str, Any]:
        return {
            **super().to_dict(include_html_tag),
            "identifier": self.identifier,
        }
